#!/bin/bash

# OrdersPage.tsx에서 Layout 관련 코드만 제거
# 1. import 제거
sed -i '3d' OrdersPage.tsx

# 2. loading return 수정 (253-255줄)
sed -i '253,255c\    return <Loading />;' OrdersPage.tsx

# 3. main return의 <Layout> 제거 (259줄)
sed -i '259d' OrdersPage.tsx

# 4. 마지막 </Layout> 제거 (673줄 근처)
# 마지막에서 3번째 줄의 </Layout> 제거
tail -n 20 OrdersPage.tsx > /tmp/orders_tail.txt
sed -i '/<\/Layout>/d' /tmp/orders_tail.txt
head -n -20 OrdersPage.tsx > /tmp/orders_head.txt
cat /tmp/orders_head.txt /tmp/orders_tail.txt > OrdersPage.tsx

echo "수정 완료"
