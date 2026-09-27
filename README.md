# Blog

Jekyll site for GitHub Pages. No build step is needed; GitHub builds it.

## Add a post
Create `_posts/YYYY-MM-DD-title.md` with front matter:

    ---
    layout: post
    title: "Your title"
    date: YYYY-MM-DD
    ---

## Publish
1. Create a public GitHub repo on the account you want.
   - Name it `<username>.github.io` to serve at `https://<username>.github.io/`, or
   - use any name and set `baseurl: "/<repo-name>"` in `_config.yml`.
2. `git add -A && git commit -m "Initial site"`
3. `git remote add origin https://github.com/<username>/<repo>.git && git push -u origin main`
4. On GitHub: Settings → Pages → Source: "Deploy from a branch", branch `main`, folder `/ (root)`.
