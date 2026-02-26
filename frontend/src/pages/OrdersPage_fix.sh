#!/bin/bash
cd /root/uvis/frontend/src/pages

# 백업
cp OrdersPage.tsx OrdersPage.tsx.broken

# Layout import가 있는지 확인
if ! grep -q "import Layout from" OrdersPage.tsx; then
    # 6번째 줄 뒤에 Layout import 추가
    sed -i '6a import Layout from '\''../components/common/Layout'\'';' OrdersPage.tsx
fi

# if (loading) 블록 찾아서 수정 (250-256줄 근처)
# 전체 if (loading) 블록을 교체
sed -i '/if (loading) {/,/^  }$/c\
  if (loading) {\
    return (\
      <Layout>\
        <Loading />\
      </Layout>\
    );\
  }' OrdersPage.tsx

# main return의 Fragment를 Layout으로 변경
# return (<> 를 return (<Layout> 으로
sed -i 's/return (<>/return (\n    <Layout>/g' OrdersPage.tsx

# 마지막 </> 를 </Layout>으로 (export 바로 위)
sed -i '/export default OrdersPage/i\  </Layout>\n  );' OrdersPage.tsx
sed -i '/export default OrdersPage/{x;/^$/!{x;s/<\/>/    /;b};x}' OrdersPage.tsx

echo "수정 완료"
