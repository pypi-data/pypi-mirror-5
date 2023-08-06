/*
  Calculate simple precision and recall measures for a set of
  corresponding boundary pairs.

  (c) 2005-2006 F.J. Estrada and A. D. Jepson, Updated May 2006


  TODO:
      - a single target, multiple source images in the command line
      - setup context correctly
      - use getopt
      - check dimensions of target and source images, must be the same
*/

#include <png.h>
#include <zlib.h>

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <ctype.h>
#include <math.h>
#include <string.h>
#include <strings.h>
#include <sys/types.h>
#include <errno.h>
#include <stdbool.h>
#include <getopt.h>


/*------------------------------------------------------------------------------
 * Constants
 *----------------------------------------------------------------------------*/

#define MY_PI 3.1415926535

/* image format */
#define IMG_FORMAT_UNKNOWN  0           /* available image formats */
#define IMG_FORMAT_PGM      1
#define IMG_FORMAT_PNG      2

#define MAX_NUM_SOURCES 256
#define MAX_FILENAME FILENAME_MAX
#define MAX_RADIUS 100
#define MAX_NUM_RADII 100

/* default values */
#define DEFAULT_RADIUS 3
#define DEFAULT_FORMAT 0
#define DEFAULT_VERBOSITY 0

/* error numbers */
#define NO_ERROR 0
#define ERROR    1
#define HALT     2

#define THIS_RELEASE           0
#define THIS_MAJOR_VERSION     0
#define THIS_MINOR_VERSION     1
#define THIS_VERSION_STRING    "0.0.1"

/*------------------------------------------------------------------------------
 * Types
 *----------------------------------------------------------------------------*/

typedef struct {
  int format;
  int width, height;
  unsigned char * data;
  char filename[MAX_FILENAME];
} imageStruct, *Image;

typedef struct {
  char * source[MAX_NUM_SOURCES];
  char * target;
  int radius[MAX_NUM_RADII];
  int num_sources;
  bool verbosity;
  bool mean;
  char * outname;
} contextStruct, *Context;


/*------------------------------------------------------------------------------
 * Macros
 *----------------------------------------------------------------------------*/

#define isnull( _ptr )                                                         \
  (NULL == (_ptr))

#define errorMsg( format, ... )                                                \
  error_msg( __LINE__, __FILE__, __func__, format, ##__VA_ARGS__ )

#define imgData( _img )                                                        \
  ((_img)->data)

#define imgWidth( _img )                                                       \
  ((_img)->width)

#define imgHeight( _img )                                                      \
  ((_img)->height)


/* various print out macros */
#define perr( _format, ... ) fprintf( stderr, _format "\n", ##__VA_ARGS__ )
#define pout( _format, ... ) fprintf( stdout, _format "\n", ##__VA_ARGS__ )
#define nout( _format, ... ) fprintf( stdout, _format, ##__VA_ARGS__ )
#define poutt( _format, ... ) fprintf( stdout, "\t" _format "\n", ##__VA_ARGS__ )
#define perrt( _format, ... ) fprintf( stderr, "\t" _format "\n", ##__VA_ARGS__ )


/*------------------------------------------------------------------------------
 * Prototypes
 *----------------------------------------------------------------------------*/

inline Image img_free( Image img ) __attribute__((always_inline));
inline Image img_new( void ) __attribute__((always_inline));
inline int iround( float x ) __attribute__((always_inline));
                           
void defaults( Context ctx );
float dist_match( Image img1, Image img2, int radius );
void error_msg( int line_number, const char * const sourcefile,                \
                const char * funcname, const char * fmt, ... );
int guess_format( const char * filename );
int parse_command_line( const int argc, char * const argv[], Context ctx );
void print_usage( void );

Image read_pgm( const char * filename );
Image read_png( const char * filename );
Image read_image( const char * filename );


/*------------------------------------------------------------------------------
 * Definitions
 *----------------------------------------------------------------------------*/


void print_usage( void )
{
  char ESC = 27;
  
  pout( " " );
  pout( "fmetric computes precision, recall, and f-metric values between target" );
  pout( "and source images for given radii values.");
  pout( " " );
  nout( "usage: " );
  printf("%c[1m",ESC);                    /*- turn on bold */
  pout( "fmetric [options] target src1 [src2 src3...]" );
  printf("%c[0m",ESC);                    /* turn off bold */
  pout( " " );
  pout( "valid options are:" );
  poutt( "-h | --help \t\t prints this help message" );
  poutt( "-m | --mean \t\t outputs mean f-metric for all radii (off)" );
  poutt( "-o | --output <filename> output file name (stdout)" );
  poutt( "-q | --quiet \t\t turn verbosity off (off by default)" );
  poutt( "-r | --radii <range> \t radii integer values (3)" );
  poutt( "-v | --verbose \t\t toogle verbosity on (off)" );
  poutt( "-V | --version \t\t prints version information and halts" );
  pout( " " );
}


void defaults( Context restrict ctx )
{
  ctx->source[0] = NULL;
  ctx->target = NULL;
  ctx->radius[0] = DEFAULT_RADIUS;
  ctx->radius[1] = 0;
  ctx->num_sources = 0;
  ctx->verbosity = false;
  ctx->outname = NULL;
  ctx->mean = false;
}

int parse_radii( char * radii_string, Context restrict ctx )
{
  /* we parse radii values in radii_string which is comma delimited, as in
     1,2-4,7-9. this is equivalent to 1,2,3,4,7,8,9. we avoid duplication of
     values, i.e., 2,2-3 returns only two radii values, 2 and 3. likewise
     1-5,3-6 is equivalent to 1-6. descending intervals are not allowed,
     i.e. A-B is only valid when A <= B; otherwise an error is caught. this
     function does not modify the input string radii_string. */
     
  int counter = 0;
  int error = NO_ERROR;
  bool done = false;
  char * delim_ptr;
  char * dash_ptr;
  char * str = radii_string;
  const char delimeter = ',';
  
  /* skip white spaces and commas if any at head of string */
  while ( isspace(*str) || *str == delimeter ) str++;
  
  /* loop over tokens */
  do {
    delim_ptr = strchr( str, delimeter );
    if ( isnull( delim_ptr )) {
      /* this should be the last token */
      delim_ptr = str;
      done = true;
    }
    else
      *delim_ptr = '\0';
    
    dash_ptr = strchr( str, '-' );    
    if ( isnull( dash_ptr )) {
      /* we have a single number */
      ctx->radius[counter++] = atoi( str );
    }
    else {
      /* we have a token in the form A-B, for A and B numbers */
      *dash_ptr = '\0';
      int start = atoi( str );
      int end = atoi( dash_ptr + 1 );
      *dash_ptr = '-';
      if ( end < start  || end < 1 || end > MAX_RADIUS
           || start < 1 || start > MAX_RADIUS ) {
        errorMsg( "invalid interval %d-%d for radius", start, end );
        error = ERROR;
        break;
      }
      while ( start <= end ) {
        ctx->radius[counter++] = start;
        start++;
      }
    }
    
    str = delim_ptr + 1;
    if ( !done ) *delim_ptr = delimeter;
  } while ( !done );
  
  /* set radius after last to zero to indicate end of entries */
  ctx->radius[counter] = 0;
  
  return error;
}

int parse_command_line( const int argc, char * const argv[],      \
                        Context restrict ctx )
{
  /*
   * a typical call is:
   *        precision -r 2-7 -m -o result.txt target.png src1.png src2.png...
   *
   */

  int error = NO_ERROR;
  int option_index = 0;
  opterr = 0;

  static char version_string[] =                            \
    "\n This is fmetric version " THIS_VERSION_STRING
    "\n Copyright (C) Alexandre Cunha, 2013\n"
    " Center for Advanced Computing Research\n"
    " California Institute of Technology\n"
    " Report bugs to cunha@caltech.edu\n"
    "\n"
    " This is an extension of original code by\n"
    " F.J. Estrada and A. D. Jepson\n"
    " Copyright (C) 2005-2006, updated May 2006.\n\0";
  
  /* both short and long option switches are available. short options are
     issued using a single dash '-' and long options uses double dashes
     '--'. this follows the usual GNU programming standards. */
  
  static char short_options[] = "vqVho:r:m";
  static struct option long_options[] = {
    {"verbose", no_argument, NULL, 'v' },
    {"quiet", no_argument, NULL, 'q' },
    {"version", no_argument, NULL, 'V'},
    {"help", no_argument, NULL, 'h'},
    {"output", required_argument, NULL, 'o'},
    {"radius", required_argument, NULL, 'r'},
    {"mean", no_argument, NULL, 'm'},
    {0, 0, 0, 0}
  };
  
  defaults( ctx );
  
  while ( !error ) {
    
    int c = getopt_long( argc, argv, short_options, long_options, &option_index );
    if ( c == -1 ) break;                 /* done with options */

    switch ( c ) {
      
    case 'h':
      print_usage();
      error = HALT;
      break;
      
    case 'V':
      pout( "%s", version_string );
      error = HALT;
      break;
      
    case 'r':
      /* identify radii to use */
      if ( !isdigit( optarg[0] )) {
        errorMsg( "invalid value for radii (%s)", optarg );
        error = ERROR;
      }
      else
        error = parse_radii( optarg, ctx );
      break;
      
    case 'o':
      //ctx->outname = optarg;
      ctx->outname = argv[optind - 1];
      break;

    case 'q':
      ctx->verbosity = false;
      break;
      
    case 'm':
      ctx->mean = true;
      break;

    case 'v':
      ctx->verbosity = true;
      break;

    case ':':
      /* missing argument to current option */
      errorMsg( "missing argument in -%c.", optopt );
      error = ERROR;
      break;
      
    case '?':
      /* an invalid switch was found */
      errorMsg( "invalid switch -%c. try -h.", optopt );
      error = ERROR;
      break;
      
    default:
      /* an invalid switch was found */
      errorMsg( "unknown switch. try again" );
      print_usage();
      error = ERROR;
      break;
    }
  }

  if ( !error ) {
    if ( (argc - optind) < 2 ) {
      errorMsg( "program needs a target and at least one source image." );
      error = ERROR;
    }
    else {
      ctx->target = argv[optind++];
      int src = 0;
      while ( optind < argc ) {
        ctx->source[src++] = argv[optind++];
      }
      ctx->source[src] = NULL;
      ctx->num_sources = src;
      
      if ( isnull(ctx->target) || isnull(ctx->source[0]) ) {
        errorMsg( "need at least a target and one source image. try again." );
        error = ERROR;
      }
    }
  }
  
  return error;
}

inline int iround( float x )
{
  return (x - (int)x > 0.5) ? ((int)x + 1) : ((int)x);
}


void error_msg( int line_number, const char * const sourcefile,
                const char * funcname, const char * fmt, ... )
{
  int verbose = 1; /* TODO */
  
  if ( verbose ) {
    va_list args;
    
    fprintf( stderr, "[%s] %s:%d: ", sourcefile, funcname, line_number );

    va_start( args, fmt );
    vfprintf( stderr, fmt, args );
    va_end( args );

    fprintf( stderr, "\n" );
  }
}

int guess_format( const char * restrict filename )
{
  char * ptr = strrchr( filename, '.' );
  if ( isnull ( ptr ))
    /* no suffix: can't determine the format */
    return IMG_FORMAT_UNKNOWN;
  
  ptr++;
  if ( 0 == strcmp( ptr, "pgm" ))
    return IMG_FORMAT_PGM;
  
  if ( 0 == strcmp( ptr, "png" ))
    return IMG_FORMAT_PNG;
  
  return IMG_FORMAT_UNKNOWN;
}

Image read_png( const char * restrict filename )
{
  unsigned int sig_read = 0;
  FILE * fp;

  /* open file for reading */
  if ((fp = fopen(filename, "rb")) == NULL)
    return NULL;

  /* make sure this is a PNG file */
  char header[8];
  int number_bytes = 8;
  fread( header, 1, number_bytes, fp );
  if ( png_sig_cmp( header, 0, number_bytes ))
    return NULL;

  /* create reading structures (thread safe) */
  png_structp png_ptr = png_create_read_struct( PNG_LIBPNG_VER_STRING, NULL, NULL, NULL );
  png_infop info_ptr  = png_create_info_struct( png_ptr );
  png_infop end_info  = png_create_info_struct( png_ptr );
  
  if ( !png_ptr ) return NULL;
  if ( !info_ptr ) {
    png_destroy_read_struct( &png_ptr, NULL, NULL );
    return NULL;
  }
  if ( !end_info ) {
    png_destroy_read_struct( &png_ptr, &info_ptr, NULL );
    return NULL;
  }

  /* read metadata (header) */
  png_set_sig_bytes( png_ptr, number_bytes );
  png_init_io( png_ptr, fp );
  png_read_info( png_ptr, info_ptr );
  
  png_uint_32 width  = png_get_image_width( png_ptr, info_ptr );
  png_uint_32 height = png_get_image_height( png_ptr, info_ptr );
  int bit_depth      = png_get_bit_depth( png_ptr, info_ptr );
  int color_type     = png_get_color_type( png_ptr, info_ptr );
  int channels       = png_get_channels( png_ptr, info_ptr );

  /* verify we are reading a gray scale image */
  if ( color_type != PNG_COLOR_TYPE_GRAY ) {
    png_destroy_read_struct( &png_ptr, &info_ptr, &end_info );
    return NULL;
  }
    
  /* convert to 8-bits/pixel image */
  if ( bit_depth < 8 )
    png_set_expand( png_ptr );

  /* create pixel data array */
  unsigned char * pixels = malloc( height * width );
  if ( isnull( pixels )) {
    errorMsg( "cannot allocate memory for %d pixels of image %s", height * width, filename );
    png_destroy_read_struct( &png_ptr, &info_ptr, &end_info );
    fclose( fp );
    return NULL;
  }
  
  /* create array of pointers to image rows and set the pointer of each row */
  png_bytep * row_pointers = png_malloc( png_ptr, height * png_sizeof(png_bytep));
  row_pointers[0] = (png_bytep)pixels;
  for ( int i = 1; i < height; ++i )
    row_pointers[i] = row_pointers[i-1] + width;
  
  /* read in pixel values */
  png_read_image( png_ptr, row_pointers );
  
  /* conclude reading */
  png_read_end( png_ptr, end_info );
  png_free( png_ptr, row_pointers );
  png_destroy_read_struct( &png_ptr, &info_ptr, &end_info );
  fclose( fp );

  /* create and return an Image */
  Image img = img_new();
  if ( isnull(img) ) {
    errorMsg( "cannot create an Image" );
    return NULL;
  }
  
  img->data = pixels;
  img->width = width;
  img->height = height;
  img->format = IMG_FORMAT_PNG;
  strcpy( img->filename, filename );
  
  return img;
}

Image read_pgm( const char * restrict fname )
{
  /*
    This function reads a PROPERLY FORMATTED .pnm file and returns a pointer
    to an array of unsigned int containing the image. Notice that no error
    checking whatsoever is performed, so use with caution!
 
    Input parameters: Name of the .pnm file
 
    Output: A pointer to an array of unsigned int, or NULL if unsuccessful
  */
    
  FILE *f;
  int d;
  unsigned char *data;  
  char line[255];
  int sizx, sizy;
  
  f=fopen(fname,"rb");
  if (f==NULL)
    {
      errorMsg( "unable to open input file %s.", fname );
      return(NULL);
    } 
 
  fgets(&line[0],254,f);
  fgets(&line[0],254,f);
  sscanf(line,"%d %d",&sizx, &sizy); /*printf("w = %d, h = %d\n", sizx, sizy );*/
  fgets(&line[0],254,f);

  fgets(&line[0],254,f);
  
  data=(unsigned char *)malloc(sizx*sizy*sizeof(unsigned char));
  if (data==NULL)
    {
      errorMsg("unable to obtain memory for image data.");
      fclose(f);
      return(NULL);
    }
  
  fread(data,sizx*sizy*sizeof(unsigned char),1,f);
  fclose(f);

  /* create and return an Image */
  Image img = img_new();
  if ( isnull(img) ) {
    errorMsg( "could not create an Image" );
    return NULL;
  }
  
  img->data = data;
  img->width = sizx;
  img->height = sizy;
  img->format = IMG_FORMAT_PGM;
  strcpy( img->filename, fname );
  
  return img;
} 

Image read_image( const char * restrict filename )
{
  Image img = NULL;
  int format = guess_format( filename );

  switch ( format ) {
  case IMG_FORMAT_PNG:
    img = read_png( filename );
    break;
  case IMG_FORMAT_PGM:
    img = read_pgm( filename );
    break;
  default:
    errorMsg( "file %s not in recognized image format", filename );
    break;
  }
  
  return img;
}

inline Image img_new( void )
{
  Image img = malloc( sizeof(imageStruct));
  if ( isnull(img) ) {
    errorMsg( "cannot malloc a imageStruct" );
    return NULL;
  }
  
  img->data = NULL;
  img->width = 0;
  img->height = 0;
  img->format = IMG_FORMAT_UNKNOWN;
  img->filename[0] = '\0';

  return img;
}

inline Image img_free( Image img )
{
  if ( !isnull( img)) {
    if ( !isnull( imgData( img )))
      free( imgData( img ));
    free( img );
    img = NULL;
  }

  return img;
}

float dist_match( Image restrict img1, Image restrict img2, int EP_rad )
{
  /*
    This function calculates the actual matching, for each
    pixel in s1, we search its neighborhood in a radius of EP_rad (see
    #define statement above) pixels, we match a boundary pixel in s1
    to any boundary pixel in s2 in this neighbornood, subject to the
    condition that no other boundary pixels in s1 should exist in between.

    Input parms: s1, pointer to an array of (sizx*sizy) unsigned chars
    containing the first boundary map (the source map),
    aything non-zero in this map is taken to be a boundary
    element

    s2, pointer to an array of (sizx*sizy) unsigned chars
    containing the second boundary map (the target map).
    Here also, any non-zero entry is taken to be a boundary
    element.

    -> special case, when our code encounters a single-label
    segmentation, the resulting boundary map is all 128's,
    we check for such an input map before computing anything.

    Return values: The number of pixels in s1 for
    which a suitable match was found in s2, divided by the
    total number of boundary pixels in s1.

  */

  float xx,yy;
  int x,y,i,j,k;
  int tpix;
  int found;
  int noBlock;
  float vx,vy;
  float len;
  float magn;
  float dist;
  int matched;
  int samedir,foundaki;
  float dist2;
  float ang2;
  float dang;
  float ux,uy;
  float d_avg;

  int sizx = imgWidth( img1 );
  int sizy = imgHeight( img1 );
  unsigned char * s1 = imgData( img1 );
  unsigned char * s2 = imgData( img2 );
  
  
  dang=MY_PI/8;	// Angle difference between sampling directions for
  // checking that a pixel in s1 is on the closest boundary
  // for its hypothesized match in s2.

  tpix=0;	// Total number of pixels
  matched=0;	// Number of matched pixels


  // Check that the segmentations are not empty of boundaries!

  if (*s1==128||*s2==128)
    {
      // AT least one of these is empty!
      errorMsg( "empty segmentation.");
      return(-1);
    }

  d_avg=0;

  /* for each pixel in s1 */
  for (x=0;x<sizx;x++)
    for (y=0;y<sizy;y++)
      {
        if (*(s1+(int)x+(((int)y)*sizx))!=0)  // There is a boundary pixel in s1 at (x,y)
          {    
            /* for each distance */
            found=0;
            tpix++;
            for (i=x-EP_rad;i<=x+EP_rad;i++)	// Square neighborhood around (x,y)
              {
                for (j=y-EP_rad;j<=y+EP_rad;j++)
                  {
                    // If the distance from (i,j) to (x,y) < EP_rad, and (i,j) are valid image
                    // coordinates, check whether there is a boundary pixel at (i,j) in s2
                    len=sqrt(((x-i)*(x-i))+((y-j)*(y-j)));
                    if (len<=EP_rad&&i>=0&&i<sizx&&j>=0&&j<sizy)
                      {
                        if (*(s2+i+(j*sizx))!=0)  // There is a boundary pixel at (i,j) in s2
                          {
                            // Check there are no other boundary pixels between (x,y) and (i,j) in
                            // s1
                            vx=(i-x);		// Get a unit vector from (x,y) to (i,j)
                            vy=(j-y);
                            magn=sqrt((vx*vx)+(vy*vy));
                            vx=vx/magn;
                            vy=vy/magn;
                            noBlock=1;

                            for (dist=1;dist<len;dist++)  // Go from (x,y) to (i,j)
                              {
                                xx=iround(x+(dist*vx));
                                yy=iround(y+(dist*vy));
                                if (xx>=0&&xx<sizx&&yy>=0&&yy<sizy) 
                                  if (*(s1+(int)xx+(((int)yy)*sizx))!=0&&xx!=i&&yy!=j)
                                    {
                                      // There is another pixel in between!
                                      noBlock=0;
                                    }
                              }
                            if (noBlock)
                              {
                                // Passed first test, no intermediate pixels, now check that (x,y)
                                // is in the direction of the closest boundary from (i,j) in s2.
                                // For that, determine the direction to the closest boundary (there
                                // may be many!) and check that the directions are similar.

                                samedir=0;
                                foundaki=0;
                                for (dist2=0;dist2<=len;dist2+=1)
                                  {
                                    for (ang2=0;ang2<2*MY_PI;ang2+=dang)
                                      {
                                        ux=cos(ang2);
                                        uy=sin(ang2);
                                        xx=i+iround((ux*dist2));
                                        yy=j+iround((uy*dist2));
                                        if (xx>=0&&xx<sizx&&yy>=0&&yy<sizy)
                                          {
                                            if (*(s1+(int)xx+(((int)yy)*sizx))!=0) // found boundary in S1
                                              {
                                                if (dist2==0&&len<=1)
                                                  {
                                                    samedir=1; // registered with same boundary
                                                    foundaki=1;
                                                  }
                                                else
                                                  {
                                                    if (dist2==0) foundaki=1;        // not same boundary
                                                    else
                                                      {
                                                        // dist2 > 0, check direction
                                                        if ((ux*vx)+(uy*vy)<-.90)
                                                          {
                                                            samedir=1;  // same side of boundary
                                                            foundaki++;
                                                          }
                                                        else foundaki++;
                                                      }
                                                  }
                                              }
                                          }
                                      } // end for (ang2...

                                    if (foundaki>0||samedir) break;

                                  } // end for (dist2...

                              } // end if (noBlock)

                            if (noBlock&&samedir)
                              {
                                // There's no intermediate pixel, and s1 is on the closest
                                // boundary to s2
                                matched++;
                                found=1;
                                d_avg+=len;
                                break;		// End loop over j!
                              }

                          } // end if (*s2...
                      } // end if (len<...
                  } // end for (j...
                if (found) break;	// End look over i
              } // End for (i...
     
          } // end if (*s1...
      } // end for (y...   
 
  /*fprintf(stdout,"Total pixels in segmentation s1 %d\n",tpix);*/
 
  if (tpix<0) 
    {
      // Empty segmentation
      return(-1);
    }
 
  d_avg=d_avg/matched;

  /*fprintf(stdout,"Matched: %d, tpix: %d, avg distance %f\n",matched,tpix,d_avg);*/
  return((float)matched/(float)tpix);

}


int main( int argc, char * argv[] )
{
  contextStruct ctx;
  Image source = NULL;
  Image target = NULL;
  
  int error = parse_command_line( argc, argv, &ctx );
  if ( error ) {
    if ( error == ERROR )
      errorMsg( "problem with command line. try --help.");
    goto finalize;
  }
  
  target = read_image( ctx.target );
  if ( isnull( target )) {
    errorMsg("unable to open target segmentation %s.", ctx.target );
    goto finalize;
  }
  
  for ( int j = 0; j < ctx.num_sources; ++j ) {
    source = read_image( ctx.source[j] );
    if ( isnull( source )) {
      errorMsg( "unable to open source segmentation %s.", ctx.source[j] );
      goto finalize;
    }
    
    float precision_sum = 0.0;
    float recall_sum = 0.0;
    float fmetric_sum = 0.0;
    float radius_sum = 0.0;
    
    int r = 0;
    while ( ctx.radius[r] > 0 ) {
      
      float precision = dist_match( target, source, ctx.radius[r] );
      float recall    = dist_match( source, target, ctx.radius[r] );
      float fmetric   = 2 * precision * recall / (precision + recall);
      
      fprintf( stdout, "%s\t %s\t %d\t %g\t %g\t %g\n", ctx.target, ctx.source[j], \
               ctx.radius[r], precision, recall, fmetric );
      
      precision_sum += precision;
      recall_sum += recall;
      fmetric_sum += fmetric;
      radius_sum += ctx.radius[r];
      r++;
    }
    
    if ( ctx.mean ) {
      precision_sum /= r;
      recall_sum /= r;
      fmetric_sum /= r;
      fprintf( stdout, "%s\t %s\t %g\t %g\t %g\t %g\n", ctx.target, ctx.source[j], \
               radius_sum / r, precision_sum, recall_sum, fmetric_sum );
    }
    
    source = img_free( source );
  }
  
 finalize:
  if ( !isnull(target))
    img_free( target );
  if ( !isnull(source))
    img_free( source );
  
  return 0;
}


#ifndef NO_PYTHON
#include "fmetric_py.h"
#endif
