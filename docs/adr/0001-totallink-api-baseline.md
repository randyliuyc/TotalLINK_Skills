# totallink-api skill 的权威基准为 LINKIIS 旧项目

TotalLINK 同时存在两个可作接口事实来源的服务端代码库：实际部署运行的 LINKIIS（旧 C# ASP.NET Web API，`randyliuyc/LINK` 仓库）和迁移项目 LINK.Core（.NET 10）。`totallink-api` skill 的接口契约文档以 **LINKIIS 为权威基准**：它描述当前真实运行系统的行为，迁移项目已拍板对齐老项目行为。唯一已知差异（DatasetResult 的 XML+GZip 二进制改造）在 endpoints.md 末节作为部署注意项单列，不混入主契约；若未来 LINK.Core 正式替代部署，届时整体重写基准并在本文标注 superseded。

考虑过以 LINK.Core 为基准被否决：文档价值在于描述现在能调通的系统；且新二进制格式有「须先升级客户端」的硬兼容约束，属于部署决策而非接口契约。
