#!/bin/bash

# 运行水印工具，自动输入参数：字体大小50，白色，右下角
echo -e "50\n1\n4" | python watermark_tool.py ./test_photo

# 检查结果
ls -la /test_photo/_watermark/