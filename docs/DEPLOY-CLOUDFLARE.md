# 部署到 Cloudflare Pages

本文只说明步骤。本次整理不执行部署，不调用生产接口，也不改线上配置。

现有 Pages 项目名是 `gamemap-sakurai`。现有域名是 `gamemap.speclab.info`。当前网站可能仍有 Cloudflare Access。不要修改、关闭或放宽这项访问保护，也不要在部署时顺手改它。

## 用哪一份目录

生产发布必须使用带图片的完整静态站点。课时页、分类页和首页保留着原来的图片路径；完整资源大约还包括原站的 webp 截图和封面 jpg。那些图片不在这份公开 Git 快照里。

不要把本仓库这份没有图片的 `site/` 当作生产目录上传。那样页面会缺图，不是正确的发布方式。

## 建议环境

- Node.js 22。部署前用 `node -v` 确认。
- 用 `npx` 调用 Wrangler，不要把 Wrangler 的登录状态或令牌写进仓库。
- 官方直接上传的形式是：在环境中提供账号编号，然后执行 `npx wrangler pages deploy <目录> --project-name=<项目名>`。说明见 [Use Direct Upload with continuous integration](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)。

## 令牌放在哪里

`CLOUDFLARE_API_TOKEN` 和 `CLOUDFLARE_ACCOUNT_ID` 只放在执行命令的本机环境中。不要写进文件，不要提交，不要配进本仓库的 GitHub Actions。本仓库的检查工作流不需要、也不应出现任何密钥。

令牌只应具备维护者打算使用的 Pages 权限。用完后按 Cloudflare 自己的方式保管或撤销，不要发到 Issue。

## 命令形状

在带图片的站点根目录执行，而不是在本仓库的无图快照上执行：

```bash
# 不要把尖括号里的内容写进 Git。账号编号从本机环境读取。
export CLOUDFLARE_ACCOUNT_ID="<账号编号>"
export CLOUDFLARE_API_TOKEN="<令牌>"
npx wrangler pages deploy <带图片的站点目录> --project-name=gamemap-sakurai
```

这会更新已有项目 `gamemap-sakurai`。执行前确认目录里图片文件真实存在，并且确认维护者确实要发布这一版。

不要把本仓库连接到会在每次推送时自动发布这份无图快照的 Git 集成。若以后要自动发布，也必须指向带图片的构建产物，并单独确认。

## 明确不做的事

- 不修改 Cloudflare Access
- 不新增或更换域名
- 不把 API token 写入仓库
- 不在 GitHub Actions 里部署
- 不把无图交接结果当作生产站点
