# Complete translation script for remaining Chinese text in frontend
$filePath = "C:\Users\20399\Desktop\VPN-final\VPN\frontend\src\views\IPDetection.vue"

# Read the file content
$content = Get-Content -Path $filePath -Raw -Encoding UTF8

# JavaScript code translations
$jsTranslations = @{
    "// 检测直连IP" = "// Detect direct IP"
    "// 检测代理IP" = "// Detect proxy IP"
    "// 获取详细信息" = "// Get detailed information"
    "// 一键检测所有" = "// One-click detect all"
    "// 复制结果" = "// Copy results"
    "// 清空结果" = "// Clear results"
    "// 检查代理状态" = "// Check proxy status"
    "// 定期检查代理状态" = "// Periodically check proxy status"
    "'无法获取'" = "'Unable to get'"
    "'直连IP检测完成'" = "'Direct IP detection completed'"
    "'直连IP检测失败'" = "'Direct IP detection failed'"
    "'网络错误: '" = "'Network error: '"
    "'请先启动代理服务'" = "'Please start proxy service first'"
    "'代理IP检测完成'" = "'Proxy IP detection completed'"
    "'代理可能未正常工作'" = "'Proxy may not be working properly'"
    "'代理IP检测失败'" = "'Proxy IP detection failed'"
    "'详细信息获取完成'" = "'Detailed info retrieved successfully'"
    "'详细信息获取失败'" = "'Failed to get detailed info'"
    "'所有检测完成'" = "'All detections completed'"
    "'检测过程中出现错误'" = "'Error occurred during detection'"
    "`直连IP: " = "`Direct IP: "
    "`代理IP: " = "`Proxy IP: "
    "`直连位置: " = "`Direct Location: "
    "`代理位置: " = "`Proxy Location: "
    "'结果已复制到剪贴板'" = "'Results copied to clipboard'"
    "'复制失败'" = "'Copy failed'"
    "'结果已清空'" = "'Results cleared'"
}

# Apply all translations
foreach ($chinese in $jsTranslations.Keys) {
    $english = $jsTranslations[$chinese]
    $content = $content -replace [regex]::Escape($chinese), $english
}

# Write back to file
Set-Content -Path $filePath -Value $content -Encoding UTF8

Write-Host "Complete IPDetection.vue JavaScript translation completed!"
