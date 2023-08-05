/*############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################*/

#define MASTER_ID "$Id$\n"

/* IFBTree - int key, float value BTree

   Implements a collection using int type keys
   and float type values
*/

/* Setup template macros */

#define PERSISTENT

#define MOD_NAME_PREFIX "IF"

#define DEFAULT_MAX_BUCKET_SIZE 120
#define DEFAULT_MAX_BTREE_SIZE 500

#include "_compat.h"
#include "intkeymacros.h"
#include "floatvaluemacros.h"

#ifdef PY3K
#define INITMODULE PyInit__IFBTree
#else
#define INITMODULE init_IFBTree
#endif
#include "BTreeModuleTemplate.c"
