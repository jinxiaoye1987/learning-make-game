# 部署到 Cloudflare Pages

本文只说明步骤。本次整理不执行部署，不调用生产接口，也不改线上配置。

现有 Pages 项目名是 `gamemap-sakurai`。现有域名是 `gamemap.speclab.info`。当前网站可能仍有 Cloudflare Access。不要修改、关闭或放宽这项访问保护，也不要在部署时顺手改它。

## 用哪一份目录

生产目录就是仓库中的 `site/`。截图和封面已经以相对路径放在这个目录里，和 HTML、样式、脚本是同一包静态文件。上传时带上这些图片，不要改到 R2、Cloudflare Images 或其他图片服务。

发布前确认静态检查通过，并且抽查页面图片能打开。本次文档不执行部署。

## 建议环境

- Node.js 22。部署前用 `node -v` 确认。
- 用 `npx` 调用 Wrangler，不要把 Wrangler 的登录状态或令牌写进仓库。
- 官方直接上传的形式是：在环境中提供账号编号，然后执行 `npx wrangler pages deploy <目录> --project-name=<项目名>`。说明见 [Use Direct Upload with continuous integration](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)。

## 令牌放在哪里

`CLOUDFLARE_API_TOKEN` 和 `CLOUDFLARE_ACCOUNT_ID` 只放在执行命令的本机环境中。不要写进文件，不要提交，不要配进本仓库的 GitHub Actions。本仓库的检查工作流不需要、也不应出现任何密钥。

令牌只应具备维护者打算使用的 Pages 权限。用完后按 Cloudflare 自己的方式保管或撤销，不要发到 Issue。

## 命令形状

在仓库根目录执行，把已经包含图片的 `site/` 作为上传目录：

```bash
# 不要把尖括号里的内容写进 Git。账号编号从本机环境读取。
export CLOUDFLARE_ACCOUNT_ID="<账号编号>"
export CLOUDFLARE_API_TOKEN="<令牌>"
npx wrangler pages deploy site --project-name=gamemap-sakurai
```

这会更新已有项目 `gamemap-sakurai`。执行前确认目录里图片文件真实存在，并且确认维护者确实要发布这一版。

不要把会自动发布的 Git 集成指到缺少 `site/` 图片的目录。若以后改为推送后自动发布，发布物仍应是包含图片的 `site/`，并单独确认。本次不执行该操作。

## 明确不做的事

- 不修改 Cloudflare Access
- 不新增或更换域名
- 不把 API token 写入仓库
- 不在 GitHub Actions 里部署
- 不把无图交接结果当作生产站点
