#ifndef CURSOR_H
#define CURSOR_H

#include "pykt.h"
#include "db.h"
#include "http.h"

typedef struct {
    PyObject_HEAD
    unsigned long int cur;
    DBObject *db;
} CursorObject;

extern PyTypeObject CursorObjectType;

#endif
