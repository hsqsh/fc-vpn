# BabelNet Landing Page 配置指南

## 启动网站

```bash
python3 -m http.server 8111
```
另一个terminal上
```bash
cloudflared tunnel run mytunnel
```

## 图片替换指南

### 1. Logo 替换
位置：头部区域的圆形 Logo
```html
<div class="card-3d w-40 h-40 mx-auto mb-6 relative floating">
    <!-- 将下面的 div 中的文本替换为你的 logo 图片 -->
    <div class="relative w-full h-full bg-gray-700/50 backdrop-blur-xl rounded-full flex items-center justify-center border border-white/20">
        <img src="path/to/your/logo.png" alt="BabelNet Logo" class="w-24 h-24 object-contain">
    </div>
</div>
```

### 2. 团队照片替换
位置："Meet Our Team" 部分
```html
<div class="card-3d aspect-[16/9] bg-gray-800 rounded-2xl overflow-hidden transform hover:scale-105 transition-all duration-700 shadow-2xl">
    <!-- 将下面的 div 替换为你的团队照片 -->
    <img src="path/to/your/team-photo.jpg" alt="BabelNet Team" class="w-full h-full object-cover">
</div>
```

### 3. 产品截图替换
位置：特性展示部分
```html
<div class="feature-image h-[80vh] mb-8 relative">
    <!-- 将下面的 div 替换为你的产品截图 -->
    <img src="path/to/your/product-screenshot.png" alt="BabelNet Screenshot" class="w-full h-full object-cover">
</div>
```

## 文字内容替换

### 1. 项目描述替换
找到以下部分并替换内容：
```html
<p class="leading-relaxed">
    <span lang="en">
        [在此处替换英文项目描述]
    </span>
    <span lang="zh">
        [在此处替换中文项目描述]
    </span>
</p>
```

### 2. 图片要求规格

1. Logo图片：
   - 建议尺寸：256x256 像素
   - 格式：PNG（支持透明背景）
   - 文件大小：< 200KB

2. 团队照片：
   - 建议尺寸：1920x1080 像素（16:9比例）
   - 格式：JPEG 或 PNG
   - 文件大小：< 1MB
   - 建议：选择光线充足、团队精神饱满的照片

3. 产品截图：
   - 建议尺寸：最小 1920x1080 像素
   - 格式：PNG（推荐）或 JPEG
   - 文件大小：< 2MB
   - 建议：选择能展示产品核心功能的界面截图

## 特殊功能说明

### 1. 语言切换
页面默认支持中英文切换，确保所有替换的文本都包含中英文版本：
```html
<span lang="en">English Text</span>
<span lang="zh">中文文本</span>
```

### 2. 关于跳转链接
1. Download 按钮当前链接到 Rickroll 视频
2. Billing 按钮当前链接到蔡徐坤视频，请注意调低音量：
   - 打开 targetWeb/index.html
   - 找到 audio 标签
   - 添加 volume="0.2" 属性或调整到合适音量

### 3. 性能优化建议
1. 所有图片都建议使用现代图片格式（如 WebP）
2. 压缩所有图片以提高加载速度
3. 考虑使用 CDN 托管图片资源

## 开发提示
- 所有图片路径使用相对路径
- 保持原有的 CSS 类名以维持动画效果
- 测试不同设备上的响应式布局
- 确保所有替换的内容都经过适当的压缩和优化
