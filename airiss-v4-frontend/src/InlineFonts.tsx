import React from 'react';

// OK체 폰트를 base64로 인라인화 (필요시 사용)
const InlineFonts: React.FC = () => {
  return (
    <style>
      {`
        /* OK체 폰트 - CDN 대안 */
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        /* 기본 폰트 설정 */
        * {
          font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
        }
        
        /* OK체 대체 클래스 */
        .ok-font-light {
          font-weight: 300;
        }
        
        .ok-font-medium {
          font-weight: 500;
        }
        
        .ok-font-bold {
          font-weight: 700;
        }
      `}
    </style>
  );
};

export default InlineFonts;
