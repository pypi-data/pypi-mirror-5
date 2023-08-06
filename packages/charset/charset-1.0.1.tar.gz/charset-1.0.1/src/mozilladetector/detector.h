#ifndef detector_h__
#define detector_h__

#include "nscore.h"
#include "nsUniversalDetector.h"

class CharSetDetector: public nsUniversalDetector {
    public:
        CharSetDetector(PRUint32 aLanguageFilter);
        ~CharSetDetector();
        
        char *DetectedCharset();
        
    protected: 
        char *_detected_charset;
        
        void Report(const char* aCharset);
};


typedef struct {
    void *obj;
} CharSetDetectorContext;


CharSetDetectorContext *charset_detector_create(PRUint32 aLanguageFilter);
void charset_detector_fee(CharSetDetectorContext * detector);
void charset_detector_handle_data(CharSetDetectorContext * detector, const char *buff, int length);
void charset_detector_data_end(CharSetDetectorContext * detector);
char* charset_detector_detected_charset(CharSetDetectorContext * detector);

char* charset_detect(const char *buff, int length);

#endif
