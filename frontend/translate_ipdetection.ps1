# PowerShell script to translate remaining Chinese text in IPDetection.vue
$filePath = "C:\Users\20399\Desktop\VPN-final\VPN\frontend\src\views\IPDetection.vue"

# Read the file content
$content = Get-Content -Path $filePath -Raw -Encoding UTF8

# Define translation mappings
$translations = @{
    "对比分析" = "Comparison Analysis"
    "IP是否变化" = "IP Changed"
    "位置是否变化" = "Location Changed"  
    "代理是否有效" = "Proxy Effective"
    "是" = "Yes"
    "否" = "No"
    "有效" = "Effective"
    "无效" = "Ineffective"
    "操作按钮区域" = "Action Button Area"
    "快捷操作" = "Quick Actions"
    "一键检测所有IP" = "One-Click Detect All IPs"
    "复制检测结果" = "Copy Detection Results"
    "清空结果" = "Clear Results"
    "检测直连IP" = "Detect Direct IP"
    "检测代理IP" = "Detect Proxy IP"
    "获取详细信息" = "Get Detailed Info"
    "一键检测所有" = "One-Click Detect All"
    "复制结果" = "Copy Results"
    "清空结果" = "Clear Results"
    "无法获取" = "Unable to get"
    "直连IP检测完成" = "Direct IP detection completed"
    "直连IP检测失败" = "Direct IP detection failed"
    "网络错误" = "Network error"
    "请先启动代理服务" = "Please start proxy service first"
    "代理IP检测完成" = "Proxy IP detection completed"
    "代理可能未正常工作" = "Proxy may not be working properly"
    "代理IP检测失败" = "Proxy IP detection failed"
    "详细信息获取完成" = "Detailed info retrieved successfully"
    "详细信息获取失败" = "Failed to get detailed info"
    "所有检测完成" = "All detections completed"
    "检测过程中出现错误" = "Error occurred during detection"
    "直连IP:" = "Direct IP:"
    "代理IP:" = "Proxy IP:"
    "直连位置:" = "Direct Location:"
    "代理位置:" = "Proxy Location:"
    "结果已复制到剪贴板" = "Results copied to clipboard"
    "复制失败" = "Copy failed"
    "结果已清空" = "Results cleared"
}

# Apply translations
foreach ($chinese in $translations.Keys) {
    $english = $translations[$chinese]
    $content = $content -replace [regex]::Escape($chinese), $english
}

# Write back to file
Set-Content -Path $filePath -Value $content -Encoding UTF8

Write-Host "IPDetection.vue translation completed!"
