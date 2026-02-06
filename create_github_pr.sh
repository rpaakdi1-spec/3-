#!/bin/bash

echo "=========================================="
echo "  GitHub Pull Request 생성 (서버용)"
echo "=========================================="
echo ""

# 변수 설정
REPO_OWNER="rpaakdi1-spec"
REPO_NAME="3-"
BASE_BRANCH="main"
HEAD_BRANCH="genspark_ai_developer"
PR_TITLE="Phase 8: Billing & Settlement Automation System"
PR_BODY_FILE="PHASE_8_PR_DESCRIPTION.md"

# 1. GitHub CLI 확인
if command -v gh &> /dev/null; then
    echo "✅ GitHub CLI 설치됨"
    echo ""
    
    # GitHub CLI로 PR 생성
    echo "PR 생성 중..."
    gh pr create \
        --repo "$REPO_OWNER/$REPO_NAME" \
        --base "$BASE_BRANCH" \
        --head "$HEAD_BRANCH" \
        --title "$PR_TITLE" \
        --body-file "$PR_BODY_FILE"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ PR 생성 완료!"
        echo ""
        echo "PR 확인:"
        echo "https://github.com/$REPO_OWNER/$REPO_NAME/pulls"
    else
        echo ""
        echo "❌ PR 생성 실패"
        echo ""
        echo "로그인이 필요하면 다음 명령 실행:"
        echo "gh auth login"
    fi
else
    echo "❌ GitHub CLI가 설치되지 않았습니다."
    echo ""
    echo "설치 방법:"
    echo ""
    echo "# CentOS/RHEL:"
    echo "sudo yum install -y yum-utils"
    echo "sudo yum-config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo"
    echo "sudo yum install gh"
    echo ""
    echo "# 또는 Ubuntu/Debian:"
    echo "sudo apt install gh"
    echo ""
    echo "설치 후 다시 이 스크립트를 실행하세요."
    echo ""
    echo "=========================================="
    echo "  대안: 웹 브라우저에서 PR 생성"
    echo "=========================================="
    echo ""
    echo "다음 URL에 접속하세요:"
    echo "https://github.com/$REPO_OWNER/$REPO_NAME/compare/$BASE_BRANCH...$HEAD_BRANCH"
    echo ""
    echo "또는:"
    echo "https://github.com/$REPO_OWNER/$REPO_NAME/pulls"
    echo ""
    echo "PR 정보:"
    echo "  Title: $PR_TITLE"
    echo "  Base: $BASE_BRANCH"
    echo "  Compare: $HEAD_BRANCH"
    echo ""
    echo "Description 복사:"
    echo "cat $PR_BODY_FILE"
fi

echo ""
