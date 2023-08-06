#ifndef prmem_h__
#define prmem_h__

#include "nscore.h"

void *PR_Malloc(PRUint32 size);
void *PR_Calloc(PRUint32 nelem, PRUint32 elsize);
void *PR_Realloc(void *ptr, PRUint32 size);
void PR_Free(void *ptr);

#define PR_DELETE(_ptr) { PR_Free(_ptr); (_ptr) = NULL; }
#define PR_FREEIF(_ptr)  if (_ptr) PR_DELETE(_ptr)

#endif
