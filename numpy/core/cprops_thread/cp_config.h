/* config.h.  Generated by configure.  */
/* config.h.in.  Generated from configure.in by autoheader.  */

/* fixme: #define values that have been commented out with //// are not used 
          in any of the files we need.
*/

#ifndef _CP_CONFIG_H
#define _CP_CONFIG_H

/* Unix specific things.
 * fixme: this ifdef can check more intelligently.  For now, it assumes any
 * non-windows platform has pthreads.
 */
#ifndef _WIN32
/* eric: This is used quite a few places but isn't valid on windows. */
/* Define to 1 if you have the <pthread.h> header file. */
#define CP_HAS_PTHREAD_H 1

/* eric: used in mempool.c.  Not valid on windows. */
/* Define to 1 if you have the `getpagesize' function. */
#define CP_HAS_GETPAGESIZE 1
#endif

/* eric: This is used in mempool.c, but I don't know how important it is... */
/* Define to 1 if PTHREAD_MUTEX_RECURSIVE works */
#define CP_HAS_PTHREAD_MUTEX_RECURSIVE 1


/* eric: used in thread.c */
/* Define to 1 if you have the `random' function. */
#define CP_HAS_RANDOM 1

/* eric: used in thread.c */
/* Define to 1 if you have the `srandom' function. */
#define CP_HAS_SRANDOM 1

/* eric: what system doesn't have this??? */
/* Define to 1 if you have the `read' function. */
#define CP_HAS_READ 1

/* eric: what system doesn't have this??? */
/* Define to 1 if you have the `write' function. */
#define CP_HAS_WRITE 1



#endif /* _CP_CONFIG_H */
