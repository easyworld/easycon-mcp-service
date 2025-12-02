# API扩展总结 / API Extension Summary

## 新增API接口 / New API Endpoints

### 1. 组合按键 / Combo Buttons
- **POST** `/press/combo` - 同时按下多个按键
  - 示例：同时按 A+B 键
  - Example: Press A+B simultaneously

### 2. 序列操作 / Sequence Operations  
- **POST** `/sequence` - 执行一系列操作并支持重复
  - 支持按钮、方向键、摇杆、等待等操作
  - 可重复执行1-100次
  - Supports button, hat, stick, wait actions
  - Repeat 1-100 times

### 3. 宏系统 / Macro System
- **POST** `/macro/save` - 保存宏
- **GET** `/macro/list` - 列出所有宏
- **GET** `/macro/{name}` - 获取宏详情
- **DELETE** `/macro/{name}` - 删除宏
- **POST** `/macro/execute` - 执行宏
  - 可保存复杂操作序列供重复使用
  - Save complex action sequences for reuse

### 4. 批量操作 / Batch Operations
- **POST** `/batch` - 批量执行多个命令
  - 一次请求执行多个不同类型的命令
  - Execute multiple different commands in one request

### 5. 设备控制 / Device Control
- **POST** `/led` - 控制LED开关
- **GET** `/version` - 获取固件版本
- **POST** `/controller/mode` - 更改手柄模式（Pro/JoyConL/JoyConR）
- **POST** `/controller/color` - 更改手柄颜色
- **POST** `/unpair` - 断开与主机的配对

### 6. 实用工具 / Utilities
- **GET** `/health` - 健康检查
- **GET** `/buttons` - 列出所有可用按钮
- **GET** `/directions` - 列出所有可用方向

## 主要功能增强 / Key Feature Enhancements

### 1. 组合按键支持 / Combo Button Support
```bash
# 同时按L+R（截图）
curl -X POST http://localhost:8000/press/combo \
  -d '{"buttons":["L","R"],"durationMs":50}'
```

### 2. 动作序列 / Action Sequences
```bash
# 按A，等待，按B，重复3次
curl -X POST http://localhost:8000/sequence \
  -d '{
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":100},
    {"type":"button","button":"B","durationMs":50}
  ],
  "repeatCount": 3
}'
```

### 3. 宏定义与执行 / Macro Definition & Execution
```bash
# 保存宏
curl -X POST http://localhost:8000/macro/save \
  -d '{
  "name": "farm_items",
  "steps": [
    {"type":"button","button":"A","durationMs":50},
    {"type":"wait","durationMs":500}
  ]
}'

# 执行宏10次
curl -X POST http://localhost:8000/macro/execute \
  -d '{"name":"farm_items","repeatCount":10}'
```

### 4. 批量命令执行 / Batch Command Execution
```bash
curl -X POST http://localhost:8000/batch \
  -d '{
  "commands": [
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"combo","buttons":["A","B"],"durationMs":100}
  ]
}'
```

## 动作类型 / Action Types

支持的动作类型 / Supported action types:

1. **button** - 单个按键
2. **combo** - 组合按键
3. **hat** - 方向键
4. **stick** - 摇杆
5. **wait** - 等待/延迟

## 应用场景 / Use Cases

### 1. 自动刷道具 / Auto Item Farming
```bash
# 创建刷道具宏并执行100次
curl -X POST http://localhost:8000/macro/save -d '{...}'
curl -X POST http://localhost:8000/macro/execute \
  -d '{"name":"farm","repeatCount":100}'
```

### 2. 复杂按键组合 / Complex Button Combos
```bash
# 游戏中的特殊技能组合
curl -X POST http://localhost:8000/sequence -d '{
  "steps": [
    {"type":"combo","buttons":["ZL","A"],"durationMs":100},
    {"type":"stick","lx":255,"ly":128,"durationMs":200},
    {"type":"button","button":"B","durationMs":50}
  ]
}'
```

### 3. 菜单导航自动化 / Menu Navigation Automation
```bash
# 自动打开设置菜单
curl -X POST http://localhost:8000/batch -d '{
  "commands": [
    {"type":"button","button":"HOME","durationMs":100},
    {"type":"wait","durationMs":1000},
    {"type":"hat","direction":"BOTTOM","durationMs":50},
    {"type":"button","button":"A","durationMs":50}
  ]
}'
```

## 技术改进 / Technical Improvements

1. **内存宏存储** - 支持保存和管理宏
2. **批量处理** - 一次API调用执行多个操作
3. **错误处理** - 更完善的错误信息和状态码
4. **类型验证** - 使用Pydantic进行请求验证
5. **API文档** - 自动生成Swagger UI文档

## API版本 / API Version

- **旧版本 / Old Version**: 1.0.0
- **新版本 / New Version**: 2.0.0

## 文档 / Documentation

- **README.md** - 完整API参考文档
- **examples.md** - 详细使用示例
- **Swagger UI** - http://localhost:8000/docs
- **ReDoc** - http://localhost:8000/redoc

## 兼容性 / Compatibility

✅ 所有旧的API接口保持不变，完全向后兼容
✅ All old API endpoints remain unchanged, fully backward compatible

## 下一步建议 / Next Steps

1. 运行服务器：`uvicorn mcp_service.server:app --reload`
2. 访问文档：http://localhost:8000/docs
3. 查看示例：参考 `examples.md`
4. 测试新功能：使用curl或Python requests库
