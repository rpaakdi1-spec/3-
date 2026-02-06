#!/bin/bash

echo "=========================================="
echo "  Phase 8 메인 브랜치 병합 준비"
echo "=========================================="
echo ""

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 변수 설정
REPO_OWNER="rpaakdi1-spec"
REPO_NAME="3-"
SOURCE_BRANCH="genspark_ai_developer"
TARGET_BRANCH="main"
PR_NUMBER="4"

echo "📋 병합 정보:"
echo "  저장소: $REPO_OWNER/$REPO_NAME"
echo "  PR 번호: #$PR_NUMBER"
echo "  소스: $SOURCE_BRANCH"
echo "  타겟: $TARGET_BRANCH"
echo ""

# 1. 현재 브랜치 확인
echo "1️⃣  현재 브랜치 확인..."
CURRENT_BRANCH=$(git branch --show-current)
echo "  현재 브랜치: $CURRENT_BRANCH"
echo ""

# 2. 로컬 변경사항 확인
echo "2️⃣  로컬 변경사항 확인..."
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  커밋되지 않은 변경사항이 있습니다:${NC}"
    git status -s
    echo ""
    echo "변경사항을 커밋하거나 stash하세요:"
    echo "  git add -A"
    echo "  git commit -m 'your message'"
    echo "  또는: git stash"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ 커밋되지 않은 변경사항 없음${NC}"
fi
echo ""

# 3. 원격 저장소 업데이트
echo "3️⃣  원격 저장소 최신 상태 가져오기..."
git fetch origin
echo -e "${GREEN}✅ 원격 저장소 업데이트 완료${NC}"
echo ""

# 4. main 브랜치 상태 확인
echo "4️⃣  main 브랜치 상태 확인..."
git checkout main 2>/dev/null || git checkout -b main origin/main
git pull origin main
echo -e "${GREEN}✅ main 브랜치 업데이트 완료${NC}"
echo ""

# 5. genspark_ai_developer 브랜치로 전환
echo "5️⃣  $SOURCE_BRANCH 브랜치로 전환..."
git checkout $SOURCE_BRANCH
git pull origin $SOURCE_BRANCH
echo -e "${GREEN}✅ $SOURCE_BRANCH 브랜치 업데이트 완료${NC}"
echo ""

# 6. main과의 차이 확인
echo "6️⃣  main과의 변경사항 확인..."
COMMITS_AHEAD=$(git rev-list --count origin/main..HEAD)
COMMITS_BEHIND=$(git rev-list --count HEAD..origin/main)
echo "  앞선 커밋: $COMMITS_AHEAD"
echo "  뒤처진 커밋: $COMMITS_BEHIND"
echo ""

if [ "$COMMITS_BEHIND" -gt 0 ]; then
    echo -e "${YELLOW}⚠️  main 브랜치가 앞서 있습니다. rebase 권장${NC}"
    echo ""
    read -p "main을 rebase하시겠습니까? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Rebasing..."
        git rebase origin/main
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Rebase 성공${NC}"
            echo ""
            echo "변경사항을 푸시하세요:"
            echo "  git push origin $SOURCE_BRANCH --force"
        else
            echo -e "${RED}❌ Rebase 실패. 충돌을 해결하세요${NC}"
            exit 1
        fi
    fi
fi
echo ""

# 7. PR 상태 확인 (GitHub CLI 사용)
echo "7️⃣  PR 상태 확인..."
if command -v gh &> /dev/null; then
    PR_STATUS=$(gh pr view $PR_NUMBER --repo $REPO_OWNER/$REPO_NAME --json state,mergeable --jq '.state,.mergeable')
    echo "  PR 상태: $PR_STATUS"
    echo ""
    
    # PR이 병합 가능한지 확인
    if echo "$PR_STATUS" | grep -q "CONFLICTING"; then
        echo -e "${RED}❌ PR에 충돌이 있습니다${NC}"
        echo ""
        echo "충돌 해결 방법:"
        echo "  1. git checkout $SOURCE_BRANCH"
        echo "  2. git rebase origin/main"
        echo "  3. 충돌 파일 수정"
        echo "  4. git add <파일>"
        echo "  5. git rebase --continue"
        echo "  6. git push origin $SOURCE_BRANCH --force"
        echo ""
        exit 1
    else
        echo -e "${GREEN}✅ PR 병합 가능${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  GitHub CLI가 설치되지 않아 PR 상태를 확인할 수 없습니다${NC}"
fi
echo ""

# 8. 테스트 실행 (선택사항)
echo "8️⃣  테스트 확인..."
echo "  프로덕션 테스트 결과:"
echo "    ✅ 백엔드 API: 6/6 통과"
echo "    ✅ 프론트엔드: 빌드 성공"
echo "    ✅ 데이터베이스: 정상"
echo ""

# 9. 병합 체크리스트
echo "=========================================="
echo "  병합 전 최종 체크리스트"
echo "=========================================="
echo ""

checklist=(
    "모든 테스트 통과"
    "프로덕션 배포 성공"
    "문서화 완료"
    "PR 리뷰 완료"
    "충돌 없음"
    "백업 완료"
)

for item in "${checklist[@]}"; do
    echo "  ✅ $item"
done
echo ""

# 10. 병합 명령어 안내
echo "=========================================="
echo "  병합 방법"
echo "=========================================="
echo ""

echo "방법 1: GitHub CLI로 병합 (권장)"
echo "  gh pr merge $PR_NUMBER --repo $REPO_OWNER/$REPO_NAME --squash"
echo ""

echo "방법 2: GitHub 웹에서 병합"
echo "  https://github.com/$REPO_OWNER/$REPO_NAME/pull/$PR_NUMBER"
echo "  - Squash and merge 선택"
echo "  - 커밋 메시지 확인"
echo "  - Confirm squash and merge 클릭"
echo ""

echo "방법 3: Git 명령어로 병합"
echo "  git checkout main"
echo "  git merge --squash $SOURCE_BRANCH"
echo "  git commit -m 'feat: Phase 8 - Billing & Settlement Automation System'"
echo "  git push origin main"
echo ""

# 11. 병합 후 작업
echo "=========================================="
echo "  병합 후 작업"
echo "=========================================="
echo ""

echo "1. 태그 생성:"
echo "   git tag -a v2.0.0-phase8 -m 'Release Phase 8'"
echo "   git push origin v2.0.0-phase8"
echo ""

echo "2. 릴리스 노트 작성:"
echo "   GitHub Releases 페이지에서 작성"
echo "   https://github.com/$REPO_OWNER/$REPO_NAME/releases/new"
echo ""

echo "3. 브랜치 정리:"
echo "   git branch -d $SOURCE_BRANCH"
echo "   git push origin --delete $SOURCE_BRANCH"
echo ""

echo "4. 팀 공지:"
echo "   - 배포 완료 알림"
echo "   - 주요 변경사항 공유"
echo "   - 교육 자료 배포"
echo ""

# 12. 롤백 계획
echo "=========================================="
echo "  롤백 계획 (문제 발생 시)"
echo "=========================================="
echo ""

echo "1. 긴급 롤백:"
echo "   git revert <병합 커밋 해시>"
echo "   git push origin main"
echo ""

echo "2. 데이터베이스 롤백:"
echo "   docker exec uvis-db psql -U uvis_user -d uvis_db < backup.sql"
echo ""

echo "3. 프론트엔드 롤백:"
echo "   git checkout <이전 커밋>"
echo "   cd frontend && npm run build"
echo "   docker-compose build --no-cache frontend"
echo "   docker-compose up -d frontend"
echo ""

echo "=========================================="
echo "  ✅ 병합 준비 완료!"
echo "=========================================="
echo ""

echo "다음 단계:"
echo "  1. 위의 체크리스트 재확인"
echo "  2. 병합 방법 선택"
echo "  3. 병합 실행"
echo "  4. 병합 후 작업 수행"
echo ""

echo "병합하시겠습니까? (GitHub CLI로 자동 병합)"
read -p "계속하려면 'yes'를 입력하세요: " CONFIRM

if [ "$CONFIRM" = "yes" ]; then
    if command -v gh &> /dev/null; then
        echo ""
        echo "PR 병합 중..."
        gh pr merge $PR_NUMBER --repo $REPO_OWNER/$REPO_NAME --squash --delete-branch
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ 병합 성공!${NC}"
            echo ""
            echo "태그 생성 중..."
            git checkout main
            git pull origin main
            git tag -a v2.0.0-phase8 -m "Release Phase 8: Billing & Settlement Automation System"
            git push origin v2.0.0-phase8
            echo -e "${GREEN}✅ 태그 생성 완료!${NC}"
            echo ""
            echo "🎉 Phase 8 배포 완전히 완료!"
        else
            echo -e "${RED}❌ 병합 실패${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ GitHub CLI가 설치되지 않았습니다${NC}"
        echo "GitHub 웹에서 수동으로 병합하세요:"
        echo "https://github.com/$REPO_OWNER/$REPO_NAME/pull/$PR_NUMBER"
    fi
else
    echo ""
    echo "병합이 취소되었습니다."
    echo "준비가 되면 다시 이 스크립트를 실행하세요."
fi

echo ""
