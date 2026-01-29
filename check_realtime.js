const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  // 콘솔 로그 캡처
  const logs = [];
  page.on('console', msg => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });
  
  try {
    console.log('페이지 로딩 중...');
    await page.goto('https://3000-i16kcdhvw5ng6rusdg7lj-ad490db5.sandbox.novita.ai', {
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    
    console.log('\n대시보드 로딩 완료');
    
    // 실시간 모니터링 링크 클릭
    console.log('\n실시간 모니터링 클릭...');
    await page.evaluate(() => {
      const links = Array.from(document.querySelectorAll('a'));
      const realtimeLink = links.find(link => link.textContent.includes('실시간 모니터링'));
      if (realtimeLink) realtimeLink.click();
    });
    
    // 로딩 대기
    await page.waitForTimeout(5000);
    
    console.log('\n=== 콘솔 로그 (실시간 모니터링 페이지) ===');
    logs.slice(-20).forEach(log => console.log(log));
    
    // 페이지 상태 확인
    const pageState = await page.evaluate(() => {
      const hasMap = document.querySelector('.leaflet-container') !== null;
      const hasMarkers = document.querySelectorAll('.leaflet-marker-icon').length;
      const hasLoading = document.querySelector('.animate-spin') !== null;
      const bodyText = document.body.innerText;
      
      return {
        hasMap,
        hasMarkers,
        hasLoading,
        bodyVisible: bodyText.substring(0, 200)
      };
    });
    
    console.log('\n=== 페이지 상태 ===');
    console.log(JSON.stringify(pageState, null, 2));
    
  } catch (error) {
    console.error('에러:', error.message);
  } finally {
    await browser.close();
  }
})();
