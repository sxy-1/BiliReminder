# 极客Python作业

为了帮助大家养成良好的代码习惯，本次作业将基于上周未完成的爬虫任务继续进行。本次作业除了关注基础功能的实现，更主要的是关注代码书写的规范性，包括：抽象，解藕，代码注释和typehint 面向对象等相关内容。作业内容在本文的最后。下面将详细讲解相关规范的案例。

<hr>


## 代码规范

### 代码注释

**背景与动机**

注释的本质是为了让阅读者快速理解代码逻辑。在函数或逻辑复杂的区域加入恰当注释，是团队协作和长期维护的重要保障。不要让注释充斥整个项目，也不要让整个项目没有注释。在难理解或者关键的地方添加注释即可。

**正面示例**

```python
def calculate_discount(price: float, discount: float) -> float:
    """
    计算折扣后的价格。
    
    参数:
    - price: 原价
    - discount: 折扣百分比（0-1之间）
    
    返回:
    - 折后价格
    """
    return price * (1 - discount)

```

 **反面示例**

```python
# 计算价格
def calculate(price, discount):
    return price * (1 - discount)
```

 **建议**

- 函数：推荐使用 Docstring 格式，说明用途、参数、返回值。
- 特殊判断或性能关键代码：添加行内注释说明“为何”而非“做什么”。



### 命名规范

**背景与动机**

清晰、统一的命名可以极大提升代码可读性和沟通效率，减少歧义。命名是代码可读性中最重要的一环。良好的命名能够**自解释代码含义**，减少文档和注释负担；而混乱的命名会导致理解困难、易出错、协作障碍。在 Python 中，我们遵循 [PEP 8](https://peps.python.org/pep-0008/#naming-conventions) 命名规范，它对不同作用的标识符制定了清晰标准。

#### **包名与模块名**

- **命名风格**：小写字母，尽量简短，用下划线分隔（但通常推荐不使用下划线）。
- **避免冗余命名**：包名本身已提供语义，函数或类命名不应重复包名内容。

```python
目录结构:
video/
    └── crawler.py      # 爬虫功能模块
        └── def start(): pass
调用方式:
from video.crawler import start
```

**反面示例**

```python
目录结构:
video/
    └── videoCrawler.py
        └── def videoCrawlerStart(): pass

# 使用方式:
from video.videoCrawler import videoCrawlerStart  # 重复且冗长
```

#### **变量命名**

- **风格**：`snake_case`
- **语义明确**：不要用 a、b、temp 等无意义命名
- **建议**：临时变量可用 i、j，其他尽量具备语义

**正面示例**

```python
user_id = 1001
video_title = "极客Python"
```

**反面示例**

```python
a = 1001
temp1 = "极客Python"
```

------

#### 函数命名

- **风格**：`snake_case`
- **动词开头**：命名应表达“行为”或“功能”
- **简洁但含义明确**

**正面示例**

```python
def fetch_video_data(): ...
def calculate_discount(price, rate): ...
```

**反面示例**

```python
def FetchVideoData(): ...  # 首字母大写不符合函数命名
def doIt(): ...  # doIt 含义模糊
```

------

#### **类命名**

- **风格**：`PascalCase`（首字母大写，单词拼接）
- **名词化**：类一般表示“对象”或“概念”

**正面示例**

```python
class VideoCrawler: ...
class UserProfile: ...
```

**反面示例**

```python
class videoCrawler: ...  # 类应使用大写驼峰
class crawl_video_data: ...  # 函数式命名不适合类
```

------

#### **常量命名**

- **风格**：`UPPER_SNAKE_CASE`
- **定义位置**：常量应集中在模块顶部或专门的配置文件中

**正面示例**

```python
API_KEY = "abc123"
MAX_RETRY_COUNT = 5
```

**反面示例**

```python
apiKey = "abc123"
maxRetry = 5
```

------

#### 总结

| 类型      | 风格               | 示例               |
| --------- | ------------------ | ------------------ |
| 包        | 全小写             | `crawler`, `utils` |
| 模块      | 全小写             | `login.py`         |
| 类        | `PascalCase`大驼峰 | `UserCrawler`      |
| 函数/变量 | `snake_case`       | `get_data()`       |
| 常量      | `UPPER_SNAKE_CASE` | `TIMEOUT_SECONDS`  |

> **命名就是文档**。清晰、一致、语义化的命名将为你的代码赢得“高可读性”这一关键品质，也为协作和后续维护打下基础。



### typehint

[Type Hint入门与初探(视频)](https://b23.tv/zZdcDQA)

**背景与动机**

Type hint 是 Python 3.5+ 引入的功能，它提高了函数的自文档性，有利于 IDE 补全、类型检查工具（如 mypy）等静态分析。虽然在python中书写函数时，对传入的变量往往是没有做类型约束的，但为了提高函数的可读性等问题，需要像其他语言一样，将变量的类型进行相关定义。

**正面示例**

```python
def get_video_title(video_id: str) -> str:
    ...
```

**反面示例**

```python
def get_video_title(video_id):
    ...
```

**建议**

- 类型提示适用于函数参数和返回值；
- 复杂类型可使用 `List`, `Dict`, `Optional` 等（需 `from typing import List`）。



### 解藕

**背景与动机**

所谓“解耦”，是指降低代码模块之间的**耦合性**。那么，什么是耦合性呢？耦合性描述的是一个模块与其他模块之间的依赖程度——如果一个模块的改动会引发多个其他模块的改动，就说明它们之间存在高度耦合。

在现代软件开发中，**降低耦合**被广泛推崇，目的是提升代码的可维护性、可拓展性和可测试性。比如大家常听到的“前后端分离”，本质上也是一种解耦实践 —— 将数据处理逻辑与界面展示逻辑分离开，使得前端和后端可以独立开发、测试与维护。

通过合理的架构设计（如抽象接口、模块划分、配置隔离等），我们可以实现高内聚、低耦合的系统结构，使代码结构更加清晰，修改和扩展更为方便。

**正面示例：使用接口与配置分离逻辑**

```python
class AbstractLogin:
    def login_with_qrcode(self): pass
    def login_with_phone(self): pass

class BilibiliLogin(AbstractLogin):
    def login_with_qrcode(self): ...
    def login_with_phone(self): ...
```

**反面示例**

```python
def login():
    # 同时处理二维码、手机、cookie 等所有逻辑
    ...
```

 **建议**

- 使用接口或基类进行功能抽象；
- 不同模块之间通过接口/中间件进行数据交换，避免相互直接调用。



### 抽象

**背景与动机**

对于重复出现的代码块、有共性类时，往往需要进行相关的抽象处理，比如将重复出现的代码块进行函数化处理，将有共性的类进行一个基础类的抽象，让新创建的相关类去满足基础类的实现，以此达到规范化的要求。

抽象能减少重复代码，提高逻辑通用性。例如，多个平台的爬虫可继承自一个抽象类，统一接口，便于拓展。

**正面示例**

```python
from abc import ABC, abstractmethod

class AbstractCrawler(ABC):
    @abstractmethod
    def start(self): pass

class BilibiliCrawler(AbstractCrawler):
    def start(self): ...
```

**反面示例**

```python
class Crawler:
    def start(self): ...
    def start_weibo(self): ...
    def start_xhs(self): ...
```

**建议**

- 面向接口编程；
- 遇到复用逻辑，先尝试函数/类的抽象；
- 避免“复制粘贴”式的类扩展。



### 小结

> 每一条规范不是“为了规范而规范”，而是对实际开发问题的回应。通过统一风格和提高代码质量，团队协作才能更顺利、项目可维护性更高。

<hr>


## 作业

本次作业以 **Playwright 爬虫实战** 为基础，重点锻炼大家的**代码规范性**、**项目结构设计能力** 和 **可拓展性思维**。

可参考demo：[Code代码](https://github.com/sxy-1/BiliReminder/tree/jx)   [GitHubPR提交 ](https://github.com/sxy-1/BiliReminder/pull/3)  [CI/CD分支测试](https://github.com/sxy-1/BiliReminder/actions/workflows/CI.yaml)

可参考开源项目: https://github.com/NanmiCoder/MediaCrawler

ps: playwright的打包存在一些问题，进行相关CD模拟即可，不要求打包的程序可执行。

### 目标

完成基础功能的同时，通过合理的抽象与架构设计，让项目具备良好的：

- 模块解耦性；
- 拓展性（支持多平台、多功能）；
- 可维护性（规范结构 + 命名 + 注释）；
- 可配置性（命令行 / 配置文件）；

### 基础功能

使用 Playwright 实现以下功能（建议优先以 **B站** 为目标平台）：

- 根据自定义KEYWORDS变量实现搜索相关视频，获取指定视频的基础信息（如标题、播放量、点赞量等）；
- 抓取评论区内容，并支持分页获取；



### 拓展功能（鼓励思考,前5项尽量实现）

为实现更高质量、可复用、可拓展的项目结构，请尽可能加入以下拓展功能：

#### 1. 合理抽象设计（多平台支持预留）

为了让程序未来可以拓展至其他平台（如 **小红书、微博、百度贴吧** 等），应对以下功能模块进行抽象设计：

- `AbstractCrawler`
  定义统一的爬虫接口，如：

  ```python
  def start(self): ...
  def search(self, keyword: str): ...
  ```

- `AbstractLogin`
  登录方式应独立封装，支持多种登录途径：

  ```python
  def login_by_qrcode(self): ...
  def login_by_cookie(self): ...
  def login_by_phone(self): ...
  ```

- `AbstractStorage`
  支持多种数据存储方案，如：

  ```python
  class ExcelStorage(AbstractStorage): ...
  class JsonStorage(AbstractStorage): ...
  class MysqlStorage(AbstractStorage): ...
  class MongoStorage(AbstractStorage): ...
  ```

通过上述抽象，可以让不同平台的 Crawler/Login/Storage 类分别继承并实现对应接口，便于后续拓展维护。

#### 2.合理的代码分层

2.合理化的代码分层，将各个相关的代码放入不同的包中，让main函数尽量的简洁，仅进行相关工具的初始化或配置加载等问题。

```python
project/
├── main.py                # 项目入口，仅负责初始化与配置加载
├── crawler/               # 各平台爬虫模块
│   └── bilibili.py
├── login/                 # 登录方式封装
├── storage/               # 数据存储模块
├── utils/                 # 工具函数模块（如日期、文本清洗）
├── config/                # 配置文件（如 config.yaml）
...
```

分层明确可以让主程序 (`main.py`) 保持简洁，同时降低模块间耦合。

#### 3. 添加命令行参数支持（cmd-args）

通过 `argparse` 等模块支持命令行参数传入配置，如：

```python
python main.py --platform bilibili --storage json --keyword "ChatGPT"
```

方便在不同环境或任务场景下快速切换配置。

#### 4. 添加日志功能（logging）

引入日志库（如 `logging` 或 `loguru`），记录项目运行信息、异常、抓取状态等内容，让调试和问题追踪更直观。

#### 5.团队协作（GitHub）

**使用 GitHub 进行版本控制与协作开发**，并模拟实际的开发团队协作流程。

联系学长加入github仓库：https://github.com/sxy-1/BiliReminder

建立自己的分支，避免直接更改`main`分支

使用 **Pull Request + Code Review** 流程合并代码，避免直接向 `main` 提交

#### 6.自动化流程( CI/CD)

利用 **GitHub Actions 实现 CI/CD 自动化流程**

通过 GitHub Actions 实现以下目标：

**CI（持续集成）**：检测仓库中的代码是否可以正确执行任务

**CD（持续交付/部署）**：发布release时自动进行打包上传(playwright打包存在问题，模拟即可)。

#### 7.数据清洗与结构化处理模块

- 对评论中的特殊字符、标签、表情等内容进行清洗；
- 将抓取的数据规范化为结构化格式（如统一时间、字段等）；
- 提供基本的情感分析接口（如用 `SnowNLP`、`TextBlob` 进行评论情绪判断）。

**拓展价值**：结合数据分析/AI 实践应用，面向后续数据处理打基础。

#### 8.数据可视化（结果输出）

- 抓取后生成简单可视化报告（如评论热词、用户分布等）；
- 使用 `matplotlib` / `pyecharts` / `plotly` 等生成图表；
- 或将结果导出为 HTML 可视化页面。

#### 9.断点续爬功能（任务状态管理）

- 通过本地缓存文件或数据库记录已完成的视频ID；
- 爬虫运行过程中自动跳过已处理的任务；
- 程序中断后可自动从断点继续运行。

**拓展价值**：提升鲁棒性，适应大规模数据采集场景。

#### 10. 📡 Web API 封装（Flask/FastAPI）

- 将爬虫逻辑封装为 RESTful API，如 `/crawl?platform=bilibili&keyword=...`
- 可结合前端页面或 Postman 测试

**拓展价值**：训练服务化部署思维，为项目上线打基础。

------

#### 11. 插件化架构设计

- 支持以“插件形式”添加新平台（如每个平台实现接口并在配置中注册）；
- 动态加载：程序读取配置文件自动加载 crawler/login/storage 实现类。

**拓展价值**：挑战架构设计能力，实现可插拔组件式爬虫框架。

------

#### 12. Email 通知

- 当程序运行完成、出错、抓取异常等情况时，自动发送通知（如邮箱）；
- 可配合日志信息或统计结果。

**拓展价值**：模拟真实服务监控场景，提升项目自动化程度。

#### 13. 单元测试支持（pytest）

为核心模块（如爬虫类、存储类）编写基本的测试用例，确保逻辑可靠性。可使用 `pytest` 工具。

#### 总结：组合推荐（按开发阶段）

| 类别 | 推荐功能                                         |
| ---- | ------------------------------------------------ |
| 初级 | 日志、配置分离、命令行参数、模块抽象             |
| 中级 | 异步/多线程、断点续爬、结构化输出、GitHub Action |
| 高级 | 插件式架构、情感分析、API 封装、可视化、通知系统 |