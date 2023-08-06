
#line 1 "engine.rl"
// Ragel file for the Title Markdown engine. Compiles to -*- C -*- code.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>


#line 10 "engine.c"
static const int titleMarkdownEngine_start = 13;
static const int titleMarkdownEngine_first_final = 13;
static const int titleMarkdownEngine_error = -1;

static const int titleMarkdownEngine_en_main = 13;


#line 9 "engine.rl"


static int putCharRaw(char **buf, size_t *bufPos, size_t *bufLen, char c) {
  if (*bufPos >= *bufLen) {
    *buf = realloc(*buf, *bufLen * 2);
    *bufLen *= 2;
    if (*buf == NULL) return 1;
  }
  (*buf)[*bufPos] = c;
  *bufPos = *bufPos + 1;
  return 0;
}

static int putStringRaw(char **buf, size_t *bufPos, size_t *bufLen, char *str) {
  char c;
  while ((c = *str++)) {
    if (putCharRaw(buf, bufPos, bufLen, c)) return 1;
  }
  return 0;
}

static int putCharEscaped(char **buf, size_t *bufPos, size_t *bufLen, char c) {
  if (c == '&') return putStringRaw(buf, bufPos, bufLen, "&amp;");
  else if (c == '<') return putStringRaw(buf, bufPos, bufLen, "&lt;");
  else if (c == '>') return putStringRaw(buf, bufPos, bufLen, "&gt;");
  else return putCharRaw(buf, bufPos, bufLen, c);
}

static int printBetween(char **buf, size_t *bufPos, size_t *bufLen, char *s, char *e) {
  while (s < e) {
    if (putCharEscaped(buf, bufPos, bufLen, *s++)) return 1;
  }
  return 0;
}


// Convert a Markdown string to HTML. Escapes any HTML that may be in it already. Takes
// pointer and length; does not treat NUL characters in any special way.
// NOTE: This allocates a new string. You must free it.
char *titleMarkdownToHtml(const char *markdown, int len, int copy) {
  char *p = (char *)markdown, *pe = p + len; char *eof = pe; int cs;
  char *ts, *te; int act;

  size_t bufLen = 1024, bufPos = 0;
  char *buf = malloc(bufLen * sizeof(char));
  if (buf == NULL) return NULL;

  char *linkStart, *linkEnd;
  char *urlStart, *urlEnd;

#define HOPEFULLY(x) if (x) goto err;
#define BUF &buf, &bufPos, &bufLen

  
#line 73 "engine.c"
	{
	cs = titleMarkdownEngine_start;
	ts = 0;
	te = 0;
	act = 0;
	}

#line 81 "engine.c"
	{
	if ( p == pe )
		goto _test_eof;
	switch ( cs )
	{
tr0:
#line 91 "engine.rl"
	{{p = ((te))-1;}{
      HOPEFULLY(putCharEscaped(BUF, *ts));
    }}
	goto st13;
tr2:
#line 86 "engine.rl"
	{te = p+1;{
      HOPEFULLY(putStringRaw(BUF, "<i>"));
      HOPEFULLY(printBetween(BUF, ts + 1, te - 1));
      HOPEFULLY(putStringRaw(BUF, "</i>"));
    }}
	goto st13;
tr8:
#line 81 "engine.rl"
	{te = p+1;{
      HOPEFULLY(putStringRaw(BUF, "<b>"));
      HOPEFULLY(printBetween(BUF, ts + 2, te - 2));
      HOPEFULLY(putStringRaw(BUF, "</b>"));
    }}
	goto st13;
tr16:
#line 66 "engine.rl"
	{ urlEnd = p; }
#line 74 "engine.rl"
	{te = p+1;{
      HOPEFULLY(putStringRaw(BUF, "<a href=\""));
      HOPEFULLY(printBetween(BUF, urlStart, urlEnd));
      HOPEFULLY(putStringRaw(BUF, "\">"));
      HOPEFULLY(printBetween(BUF, linkStart, linkEnd));
      HOPEFULLY(putStringRaw(BUF, "</a>"));
    }}
	goto st13;
tr20:
#line 91 "engine.rl"
	{te = p+1;{
      HOPEFULLY(putCharEscaped(BUF, *ts));
    }}
	goto st13;
tr23:
#line 91 "engine.rl"
	{te = p;p--;{
      HOPEFULLY(putCharEscaped(BUF, *ts));
    }}
	goto st13;
tr25:
#line 81 "engine.rl"
	{te = p;p--;{
      HOPEFULLY(putStringRaw(BUF, "<b>"));
      HOPEFULLY(printBetween(BUF, ts + 2, te - 2));
      HOPEFULLY(putStringRaw(BUF, "</b>"));
    }}
	goto st13;
tr27:
#line 74 "engine.rl"
	{te = p;p--;{
      HOPEFULLY(putStringRaw(BUF, "<a href=\""));
      HOPEFULLY(printBetween(BUF, urlStart, urlEnd));
      HOPEFULLY(putStringRaw(BUF, "\">"));
      HOPEFULLY(printBetween(BUF, linkStart, linkEnd));
      HOPEFULLY(putStringRaw(BUF, "</a>"));
    }}
	goto st13;
st13:
#line 1 "NONE"
	{ts = 0;}
	if ( ++p == pe )
		goto _test_eof13;
case 13:
#line 1 "NONE"
	{ts = p;}
#line 159 "engine.c"
	switch( (*p) ) {
		case 42: goto tr21;
		case 91: goto tr22;
	}
	goto tr20;
tr21:
#line 1 "NONE"
	{te = p+1;}
	goto st14;
st14:
	if ( ++p == pe )
		goto _test_eof14;
case 14:
#line 173 "engine.c"
	if ( (*p) == 42 )
		goto st1;
	goto st0;
st0:
	if ( ++p == pe )
		goto _test_eof0;
case 0:
	if ( (*p) == 42 )
		goto tr2;
	goto st0;
st1:
	if ( ++p == pe )
		goto _test_eof1;
case 1:
	if ( (*p) == 42 )
		goto st4;
	goto st2;
st2:
	if ( ++p == pe )
		goto _test_eof2;
case 2:
	if ( (*p) == 42 )
		goto st3;
	goto st2;
st3:
	if ( ++p == pe )
		goto _test_eof3;
case 3:
	if ( (*p) == 42 )
		goto st15;
	goto st2;
st15:
	if ( ++p == pe )
		goto _test_eof15;
case 15:
	if ( (*p) == 42 )
		goto tr8;
	goto tr25;
st4:
	if ( ++p == pe )
		goto _test_eof4;
case 4:
	if ( (*p) == 42 )
		goto st5;
	goto st2;
st5:
	if ( ++p == pe )
		goto _test_eof5;
case 5:
	if ( (*p) == 42 )
		goto tr8;
	goto tr0;
tr22:
#line 1 "NONE"
	{te = p+1;}
	goto st16;
st16:
	if ( ++p == pe )
		goto _test_eof16;
case 16:
#line 234 "engine.c"
	if ( (*p) == 93 )
		goto tr23;
	goto tr26;
tr26:
#line 67 "engine.rl"
	{ linkStart = p; }
	goto st6;
st6:
	if ( ++p == pe )
		goto _test_eof6;
case 6:
#line 246 "engine.c"
	if ( (*p) == 93 )
		goto tr10;
	goto st6;
tr10:
#line 67 "engine.rl"
	{ linkEnd = p; }
	goto st7;
st7:
	if ( ++p == pe )
		goto _test_eof7;
case 7:
#line 258 "engine.c"
	if ( (*p) == 40 )
		goto st8;
	goto tr0;
st8:
	if ( ++p == pe )
		goto _test_eof8;
case 8:
	switch( (*p) ) {
		case 40: goto tr13;
		case 41: goto tr0;
	}
	goto tr12;
tr12:
#line 66 "engine.rl"
	{ urlStart = p; }
	goto st9;
st9:
	if ( ++p == pe )
		goto _test_eof9;
case 9:
#line 279 "engine.c"
	switch( (*p) ) {
		case 40: goto st10;
		case 41: goto tr16;
	}
	goto st9;
st10:
	if ( ++p == pe )
		goto _test_eof10;
case 10:
	switch( (*p) ) {
		case 40: goto st12;
		case 41: goto tr16;
	}
	goto st11;
st11:
	if ( ++p == pe )
		goto _test_eof11;
case 11:
	switch( (*p) ) {
		case 40: goto st12;
		case 41: goto tr19;
	}
	goto st11;
tr13:
#line 66 "engine.rl"
	{ urlStart = p; }
	goto st12;
st12:
	if ( ++p == pe )
		goto _test_eof12;
case 12:
#line 311 "engine.c"
	if ( (*p) == 41 )
		goto tr16;
	goto st12;
tr19:
#line 66 "engine.rl"
	{ urlEnd = p; }
	goto st17;
st17:
	if ( ++p == pe )
		goto _test_eof17;
case 17:
#line 323 "engine.c"
	if ( (*p) == 41 )
		goto tr16;
	goto tr27;
	}
	_test_eof13: cs = 13; goto _test_eof; 
	_test_eof14: cs = 14; goto _test_eof; 
	_test_eof0: cs = 0; goto _test_eof; 
	_test_eof1: cs = 1; goto _test_eof; 
	_test_eof2: cs = 2; goto _test_eof; 
	_test_eof3: cs = 3; goto _test_eof; 
	_test_eof15: cs = 15; goto _test_eof; 
	_test_eof4: cs = 4; goto _test_eof; 
	_test_eof5: cs = 5; goto _test_eof; 
	_test_eof16: cs = 16; goto _test_eof; 
	_test_eof6: cs = 6; goto _test_eof; 
	_test_eof7: cs = 7; goto _test_eof; 
	_test_eof8: cs = 8; goto _test_eof; 
	_test_eof9: cs = 9; goto _test_eof; 
	_test_eof10: cs = 10; goto _test_eof; 
	_test_eof11: cs = 11; goto _test_eof; 
	_test_eof12: cs = 12; goto _test_eof; 
	_test_eof17: cs = 17; goto _test_eof; 

	_test_eof: {}
	if ( p == eof )
	{
	switch ( cs ) {
	case 14: goto tr23;
	case 0: goto tr0;
	case 1: goto tr0;
	case 2: goto tr0;
	case 3: goto tr0;
	case 15: goto tr25;
	case 4: goto tr0;
	case 5: goto tr0;
	case 16: goto tr23;
	case 6: goto tr0;
	case 7: goto tr0;
	case 8: goto tr0;
	case 9: goto tr0;
	case 10: goto tr0;
	case 11: goto tr0;
	case 12: goto tr0;
	case 17: goto tr27;
	}
	}

	}

#line 98 "engine.rl"


  HOPEFULLY(putCharRaw(BUF, '\0'));
  if (copy) {
    char *oldBuf = buf;
    buf = strdup(buf);
    free(oldBuf);
  }
  return buf;
 err:
  if (buf != NULL) free(buf);
  return NULL;
}


#if 0
int main(int argc, char **argv) {
  if (argc != 2) {
    fprintf(stderr, "usage: %s [text]\n", argv[0]);
    exit(1);
  }

  char *result = titleMarkdownToHtml(argv[1], strlen(argv[1]), 1);
  if (result != NULL) {
    puts(result);
    free(result);
    return 0;
  }

  fprintf(stderr, "%s: could not allocate memory\n", argv[0]);
  return 1;
}
#endif
