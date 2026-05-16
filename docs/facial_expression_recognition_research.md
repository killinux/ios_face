# 表情识别（Facial Expression Recognition）技术调研报告

> 调研时间：2026-05-16
> 调研目标：梳理行业内表情识别最优方案，为 iOS 端表情识别功能提供技术选型参考

---

## 1. 概述

表情识别（Facial Expression Recognition, FER）是计算机视觉领域的重要研究方向，旨在从人脸图像或视频中自动识别情绪状态。当前主流分类体系包括：

- **基本表情（6/7 类）**：Happy、Sad、Angry、Surprise、Fear、Disgust、Neutral（Contempt）
- **效价-唤醒度连续模型（VA）**：Valence（正负情绪）+ Arousal（激活程度）
- **Action Unit（AU）编码**：基于 FACS 系统的面部肌肉动作单元组合

---

## 2. 主流技术路线

### 2.1 基于 CNN 的方法

早期深度学习方法以 CNN 为主干网络，代表工作：

| 方法 | 年份 | 核心思路 | RAF-DB | AffectNet-7 |
|------|------|---------|--------|-------------|
| SCN | 2020 | 自修正网络，抑制标签噪声 | 88.14% | 63.40% |
| RUL | 2021 | 相对不确定性学习 | 88.98% | — |
| DMUE | 2021 | 双分支多不确定性估计 | 89.42% | 63.11% |
| EAC | 2022 | 擦除注意力一致性，处理歧义样本 | 90.35% | 65.32% |
| MA-Net | 2021 | 多注意力网络 | 88.42% | 64.53% |

**优势**：成熟稳定，推理速度快，适合移动端部署
**局限**：局部特征建模能力有限，难以捕捉全局上下文关系

### 2.2 基于 Vision Transformer 的方法（当前 SOTA）

Transformer 架构在 FER 领域取得显著突破：

| 方法 | 年份 | 核心思路 | RAF-DB | AffectNet-7 |
|------|------|---------|--------|-------------|
| POSTER++ | 2023 | 金字塔交叉融合 Transformer，landmark + image 双流 | 92.21% | 67.49% |
| APViT | 2022 | 情感先验注意力 + ViT | 91.98% | 66.91% |
| S-Former | 2023 | 对比学习 + Transformer | 92.01% | 66.58% |
| DAN | 2023 | 多头注意力 + 注意力蒸馏 | 92.05% | 65.69% |
| TransFER | 2022 | 多注意力 dropping + Transformer | 90.91% | 66.23% |

**优势**：全局建模能力强，精度最高
**局限**：计算量大，直接部署到移动端需要量化或蒸馏

### 2.3 基于 Foundation Model 的方法（2024-2025 前沿）

利用大规模预训练模型的迁移能力：

#### 2.3.1 CLIP-based 方法

- **EmoCLIP**：利用 CLIP 视觉-语言对齐，通过情感描述 prompt 实现零样本/少样本表情识别
- **CLIPER**：设计情感相关的 prompt 模板，在 CLIP 基础上做 prompt tuning
- **FaRL**：微软发布的面部表示学习模型，在面部相关任务上表现优异

#### 2.3.2 自监督预训练

- **MAE (Masked Autoencoder)**：掩码自编码预训练 → FER 微调
- **DINOv2**：自蒸馏预训练，提取通用视觉特征用于 FER
- **Face-DINO**：在大规模人脸数据上做 DINO 预训练，学习面部表示

#### 2.3.3 多模态大模型

- **GPT-4V / GPT-4o**：通过视觉理解直接描述表情和情绪，适合复合情绪分析
- **Qwen-VL / InternVL**：开源多模态模型，可部署私有化
- **AffectGPT**：专门针对情感计算的多模态模型

**优势**：泛化能力极强，支持开放域情绪描述
**局限**：模型体量大，延迟高，不适合实时端侧应用

### 2.4 Action Unit (AU) 分析路线

基于 FACS（Facial Action Coding System）的细粒度面部分析：

| 工具/方法 | 特点 |
|-----------|------|
| OpenFace 2.0 | 开源，支持 17 个 AU 检测 + 强度估计 |
| JAA-Net | 联合 AU 检测与表情分类，端到端训练 |
| LP-Net | 局部-整体分块网络 |
| ME-GraphAU | 图神经网络建模 AU 关系 |
| Apple ARKit | 52 个 blendshape 系数，设备端实时 |

**优势**：可解释性强，支持细粒度情感分析、微表情检测
**局限**：AU 标注成本高，从 AU 到情绪的映射规则复杂

### 2.5 视频序列方法（动态表情识别）

利用时序信息进行表情识别：

| 方法 | 年份 | 核心思路 | DFEW-UAR |
|------|------|---------|----------|
| Former-DFER | 2023 | Transformer 时序建模 | 65.70% |
| NR-DFERNet | 2023 | 噪声鲁棒动态 FER | 68.19% |
| M3DFEL | 2023 | 多模态多实例动态 FER | 69.25% |
| UniLearn | 2024 | 统一学习框架 | 69.81% |

**关键数据集**：DFEW、FERV39k、MAFW（多标签）

---

## 3. 核心技术挑战与解决方案

### 3.1 标签噪声与歧义

表情标注主观性强，标注者之间一致性低（inter-annotator agreement 约 60-70%）。

**解决方案**：
- **标签分布学习（LDL）**：将硬标签转为概率分布，反映表情的歧义性
- **SCN 自修正网络**：训练过程中动态调整样本权重，抑制噪声样本
- **EAC**：通过翻转一致性检测不确定样本，针对性处理
- **Re-labeling**：如 FER+ 对 FER2013 进行多人重标注

### 3.2 类别不平衡

实际数据中 Happy/Neutral 占比远高于 Fear/Contempt。

**解决方案**：
- **Focal Loss**：降低易分类样本权重
- **LDAM Loss**：基于标签分布的 margin loss
- **类别重采样**：过采样少数类 / 欠采样多数类
- **数据增强**：对少数类做针对性增强（mixup、cutout）

### 3.3 遮挡与大角度

口罩、墨镜、手部遮挡、极端姿态影响识别。

**解决方案**：
- **区域注意力**：对面部不同区域独立建模，被遮挡区域权重降低
- **面部分块**：将面部划分为 patch，仅利用可见 patch
- **3D 人脸重建辅助**：通过 3DMM 重建正脸视角
- **合成遮挡增强**：训练时随机遮挡面部区域提升鲁棒性

### 3.4 跨域泛化

实验室数据（CK+、Oulu-CASIA）与真实场景数据分布差异大。

**解决方案**：
- **域自适应**：DANN、MMD 等对齐源域与目标域特征分布
- **对比学习预训练**：在大规模无标注人脸数据上学习域不变特征
- **元学习**：学习跨域快速适应的能力
- **合成数据**：利用 GAN/Diffusion 生成多样化训练数据

### 3.5 微表情识别

持续时间 1/25s - 1/5s，动作幅度极小。

**解决方案**：
- **光流放大**：EVM（Eulerian Video Magnification）放大面部微运动
- **高帧率采集**：200fps+ 摄像头捕捉瞬时变化
- **时序对比学习**：学习微小时序变化的表示
- **Apex Frame 检测**：定位微表情峰值帧进行分析

---

## 4. 主要数据集

### 4.1 静态图像数据集

| 数据集 | 规模 | 类别 | 特点 |
|--------|------|------|------|
| AffectNet | ~450K | 7/8 类 + VA | 最大的野外表情数据集 |
| RAF-DB | ~30K | 7 基本 + 12 复合 | 真实场景，标注质量高 |
| FER2013 / FER+ | ~35K | 7 类 | 经典 benchmark，噪声大 |
| ExpW | ~91K | 7 类 | 网络图片，多样性高 |
| EmotioNet | ~1M | AU 标注 | 大规模 AU 数据 |

### 4.2 视频数据集

| 数据集 | 规模 | 类别 | 特点 |
|--------|------|------|------|
| DFEW | 16K clips | 7 类 | 电影片段，野外场景 |
| FERV39k | 39K clips | 7 类 | 大规模视频 FER |
| MAFW | 10K clips | 11 类 | 多标签标注 |
| CK+ | 593 seq | 7 类 | 实验室采集，经典 |
| CASME II | 256 seq | 5 类 | 微表情数据集 |

### 4.3 AU 数据集

| 数据集 | 规模 | AU 数量 | 特点 |
|--------|------|---------|------|
| BP4D | 328 video | 12 AU | 自发表情 |
| DISFA | 27 video | 12 AU | AU 强度标注 |
| GFT | 96 video | 10 AU | 多种任务场景 |
| EmotioNet | ~1M image | 12 AU | 大规模自动标注 |

---

## 5. 商业方案对比

### 5.1 国内厂商

| 厂商 | 产品 | 能力 | 适用场景 |
|------|------|------|---------|
| 旷视 Face++ | 情绪识别 API | 7 基本表情 + 多维情绪值 | 云端调用，支持视频流 |
| 百度 AI | 人脸检测与属性分析 | 表情分类 + AU 检测 | 云/端部署 |
| 腾讯优图 | 人脸分析 | 表情属性，集成微信生态 | 社交/娱乐场景 |
| 商汤科技 | SenseTime FER | 高精度表情识别 | 智慧城市/车载 |
| 虹软 ArcFace | 人脸属性 SDK | 嵌入式设备友好 | 离线端侧部署 |

### 5.2 国际厂商

| 厂商 | 产品 | 能力 | 适用场景 |
|------|------|------|---------|
| Microsoft Azure | Face API | 8 类情绪概率 | 云端，已逐步限制通用情绪检测 |
| Amazon | Rekognition | 8 类表情 + 置信度 | AWS 生态 |
| Affectiva (Smart Eye) | Emotion AI | 20+ AU 实时检测 | 车载驾驶员监控 |
| Noldus | FaceReader | 7 表情 + AU + 效价 | 学术/用户研究 |
| iMotions | 生物传感平台 | 多模态情感分析 | 市场调研 |

### 5.3 设备端方案

| 平台 | 能力 | 特点 |
|------|------|------|
| Apple ARKit | 52 blendshape 系数 | TrueDepth 相机，实时 60fps |
| Apple Vision Framework | 面部 landmark + 属性 | 不依赖深度相机 |
| Google ML Kit | 面部检测 + 表情概率 | 跨平台，轻量 |
| MediaPipe | 478 点 landmark + blendshape | 开源，跨平台 |

---

## 6. iOS 端技术选型分析

### 6.1 方案一：Apple 原生框架（推荐首选）

**技术栈**：ARKit + Vision Framework

**架构**：
```
TrueDepth Camera → ARKit Face Tracking → 52 Blendshape Coefficients → 规则/轻量模型映射 → 表情类别
```

**优势**：
- 零额外模型体积，系统内置
- 实时性极佳（60fps）
- 隐私合规（数据不出设备）
- 3D 面部追踪，抗遮挡能力强
- 52 维 blendshape 表达能力丰富

**局限**：
- 依赖 TrueDepth 相机（iPhone X 及以上前置）
- blendshape 到表情的映射需要设计规则或训练轻量分类器
- 不支持后置摄像头场景

**实现思路**：
1. 获取 `ARFaceAnchor.blendShapeLocation` 的 52 维系数
2. 设计基于规则的表情判定（如 `mouthSmileLeft + mouthSmileRight > 0.5 → Happy`）
3. 或训练一个小型 MLP/决策树做 blendshape → 表情分类

### 6.2 方案二：Core ML 自定义模型

**技术栈**：Core ML + 自训练模型

**架构**：
```
Camera Frame → Vision Face Detection → Crop & Align → Core ML Model → 表情类别 + 置信度
```

**推荐模型选择**：

| 模型 | 参数量 | 延迟（iPhone 15） | 精度参考 |
|------|--------|-------------------|---------|
| MobileNetV3-Small | 2.5M | ~3ms | ~85% (RAF-DB) |
| EfficientNet-B0 | 5.3M | ~5ms | ~88% (RAF-DB) |
| MobileFaceNet | 1.0M | ~2ms | ~86% (RAF-DB) |
| EfficientFormer-L1 | 12M | ~8ms | ~90% (RAF-DB) |

**训练流程**：
1. 使用 AffectNet + RAF-DB 联合训练
2. 知识蒸馏：POSTER++ (teacher) → MobileNet (student)
3. 量化：FP32 → INT8（Core ML 支持）
4. 导出：PyTorch → ONNX → Core ML (.mlmodel / .mlpackage)

**优势**：
- 精度可控，可针对业务场景优化
- 支持前后摄像头
- 模型体积小（1-5MB）

**局限**：
- 需要训练和维护模型
- 2D 分析，大角度/遮挡时性能下降

### 6.3 方案三：混合方案（推荐高精度场景）

**技术栈**：ARKit + Core ML

**架构**：
```
前置：ARKit 3D Tracking → Blendshape + Core ML 融合决策
后置：Vision Detection → Core ML 独立推理
```

**融合策略**：
- 前置摄像头：ARKit blendshape 特征 + CNN 图像特征 → 融合分类器
- 后置摄像头：退化为纯 Core ML 推理
- 置信度加权：根据面部角度/遮挡程度动态调整两路权重

### 6.4 方案对比总结

| 维度 | 方案一（ARKit） | 方案二（Core ML） | 方案三（混合） |
|------|----------------|------------------|---------------|
| 开发成本 | 低 | 中 | 高 |
| 精度 | 中高 | 高 | 最高 |
| 实时性 | 极佳（60fps） | 优（30fps+） | 优（30fps+） |
| 设备兼容性 | iPhone X+ 前置 | 全设备 | 全设备（降级） |
| 模型体积 | 0 | 1-5MB | 1-5MB |
| 隐私合规 | 完全设备端 | 完全设备端 | 完全设备端 |
| 可扩展性 | 有限 | 强 | 强 |

---

## 7. 推荐技术方案

### 7.1 短期（MVP 阶段）

**推荐方案一：ARKit 原生方案**

- 快速验证产品逻辑
- 利用 52 blendshape 做规则映射
- 支持 7 基本表情分类
- 开发周期：1-2 周

### 7.2 中期（精度优化）

**推荐方案二：Core ML 自定义模型**

- 在 AffectNet 上训练 EfficientNet-B0
- 知识蒸馏压缩模型
- Core ML 部署，支持 Neural Engine 加速
- 开发周期：3-4 周（含数据准备和训练）

### 7.3 长期（全面方案）

**推荐方案三：混合融合方案**

- ARKit + Core ML 双路融合
- 支持复合情绪识别
- 加入时序建模（视频级别）
- 持续迭代优化
- 开发周期：6-8 周

---

## 8. 开源资源推荐

### 8.1 模型与代码

| 项目 | 地址 | 说明 |
|------|------|------|
| POSTER++ | github.com/talented-q/poster_v2 | 当前静态 FER SOTA |
| DAN | github.com/yaoing/DAN | 多注意力网络 |
| face.evoLVe | github.com/ZhaoJ9014/face.evoLVe | 人脸分析工具库 |
| OpenFace 2.0 | github.com/TadasBaltrusaitis/OpenFace | AU 检测开源工具 |
| MediaPipe | github.com/google/mediapipe | 跨平台面部分析 |
| HSEmotion | github.com/HSE-asavchenko/face-emotion-recognition | 轻量级 FER，适合移动端 |

### 8.2 数据集获取

- AffectNet：需申请，mohammad.affectnet@gmail.com
- RAF-DB：http://www.whdeng.cn/raf/model1.html
- FER+：github.com/microsoft/FERPlus
- DFEW：需申请，联系作者

---

## 9. 结论与建议

1. **精度优先**选 POSTER++/Transformer 路线 + 知识蒸馏到移动端
2. **速度优先**选 ARKit 原生 blendshape 方案
3. **平衡方案**选 EfficientNet-B0 + Core ML，兼顾精度与性能
4. **标签噪声**是 FER 核心问题，训练时务必采用 LDL 或 SCN 策略
5. **数据**方面建议 AffectNet + RAF-DB 联合训练，配合亚洲面孔数据做 domain adaptation
6. **隐私合规**建议全链路设备端推理，不上传面部数据

---

## 附录 A：关键术语

| 术语 | 全称 | 说明 |
|------|------|------|
| FER | Facial Expression Recognition | 面部表情识别 |
| FACS | Facial Action Coding System | 面部动作编码系统 |
| AU | Action Unit | 动作单元 |
| VA | Valence-Arousal | 效价-唤醒度 |
| LDL | Label Distribution Learning | 标签分布学习 |
| RAF-DB | Real-world Affective Faces Database | 真实场景表情数据库 |
| DFEW | Dynamic FER in the Wild | 野外动态表情识别 |
| Blendshape | — | 面部形变系数 |

## 附录 B：参考文献

1. Li, S., & Deng, W. (2022). Deep Facial Expression Recognition: A Survey. IEEE TAFFC.
2. Xue, F., et al. (2023). POSTER++: A simpler and stronger facial expression recognition network. arXiv:2301.12149.
3. Wen, Z., et al. (2023). DAN: Distract Your Attention Network. arXiv:2301.12149.
4. Zhang, Y., et al. (2022). Learn from All: Erasing Attention Consistency for Noisy Label FER. ECCV 2022.
5. Savchenko, A. (2022). HSEmotion: High-Speed Emotion Recognition for Mobile. arXiv:2211.04228.
6. Apple Developer Documentation. ARKit - Face Tracking. developer.apple.com.
7. Mollahosseini, A., et al. (2019). AffectNet: A Database for Facial Expression, Valence, and Arousal. IEEE TAFFC.
