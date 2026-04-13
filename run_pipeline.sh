#!/bin/bash
# DeepPresenter PPT 工作流 - 一键运行脚本
# 用法: ./run_pipeline.sh

set -e

# 配置
INPUT_DIR="${INPUT_DIR:-input}"
OUTPUT_DIR="${OUTPUT_DIR:-output}"
SLIDES_DIR="${SLIDES_DIR:-slides}"
SCREENSHOTS_DIR="${SCREENSHOTS_DIR:-screenshots}"

# API 配置（从环境变量或 config.yaml 读取）
export TEXT_API_ENDPOINT="${TEXT_API_ENDPOINT:-}"
export TEXT_API_KEY="${TEXT_API_KEY:-}"
export IMAGE_API_ENDPOINT="${IMAGE_API_ENDPOINT:-}"
export IMAGE_API_KEY="${IMAGE_API_KEY:-}"

echo "=========================================="
echo "  DeepPresenter PPT 工作流"
echo "=========================================="

# 检查依赖
check_dep() {
    if ! command -v $1 &> /dev/null; then
        echo "错误: 缺少 $1"
        echo "安装: $2"
        exit 1
    fi
}

check_dep "python3" "brew install python@3.11"
check_dep "node" "brew install node"

echo ""
echo "[1/5] 读取知识库 → 生成大纲"
python3 scripts/analyze_content.py \
    --input "$INPUT_DIR" \
    --output "$OUTPUT_DIR/outline.md" \
    --api "${TEXT_API_ENDPOINT}" \
    --key "${TEXT_API_KEY}"

echo ""
echo "[2/5] 生成 HTML 设计稿"
python3 scripts/generate_html.py \
    --outline "$OUTPUT_DIR/outline.md" \
    --output "$SLIDES_DIR"

echo ""
echo "[3/5] 安装 html2pptx（如需要）"
if ! command -v html2pptx &> /dev/null; then
    npm install -g html2pptx
fi

echo ""
echo "[4/5] HTML → 标准 PPTX"
html2pptx --input "$SLIDES_DIR" --output "$OUTPUT_DIR/final.pptx" --template modern 2>/dev/null || \
    echo "  (html2pptx 转换失败，跳过)"

echo ""
echo "[5/5] 分层截图 + 组装"
if command -v playwright &> /dev/null; then
    python3 scripts/screenshot_layers.py --slides "$SLIDES_DIR" --output "$SCREENSHOTS_DIR"
    
    python3 scripts/assemble_layered.py \
        --screenshots "$SCREENSHOTS_DIR" \
        --slides "$SLIDES_DIR" \
        --output "$OUTPUT_DIR/layered.pptx"
else
    echo "  (Playwright 未安装，跳过分层功能)"
fi

echo ""
echo "=========================================="
echo "  完成！"
echo "=========================================="
echo "标准 PPTX: $OUTPUT_DIR/final.pptx"
echo "分层 PPTX: $OUTPUT_DIR/layered.pptx"
