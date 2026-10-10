<div dir="rtl">

# راهنمای کامل راه‌اندازی Email-OSINT- (از صفر، برای مبتدی)

این راهنما قدم‌به‌قدم است. قبل از هر دستور می‌گویم **چه کار می‌کند** و **چه خروجی‌ای باید ببینید**.
خروجی‌هایی که با برچسب «(خروجی واقعی)» آمده‌اند واقعاً هنگام ساخت همین مخزن اجرا و کپی شده‌اند.
جاهایی که چیزی را نتوانستم خودم آزمایش کنم، صریحاً نوشته‌ام «آزمایش نشده».

> قرارداد: دستورهایی که با `PS>` شروع می‌شوند را در **PowerShell ویندوز** بزنید.
> بقیهٔ دستورها را در **ترمینال اوبونتو (WSL)** بزنید. خودِ `PS>` یا `$` را تایپ نکنید.

---

## اطلاعات تأییدشدهٔ ابزارها (تاریخ بررسی: ۲۰۲۶-۱۰-۱۰)

| ابزار | ستاره‌ها | آخرین تگ | تاریخ آخرین کامیت (master) | نسخهٔ قفل‌شده در این مخزن | مجوز نسخهٔ قفل‌شده |
|---|---|---|---|---|---|
| [SpiderFoot](https://github.com/smicallef/spiderfoot) | 23.3k | `v4.0` (۲۰۲۲-۰۴-۰۷) | ۲۰۲۳-۱۱-۰۵ | `v4.0` → `b9c345d` | **GPL-2.0** (نکتهٔ مهم پایین را ببینید) |
| [Sherlock](https://github.com/sherlock-project/sherlock) | 93.8k | `v0.16.2` (۲۰۲۶-۰۹-۰۸) | ۲۰۲۶-۰۹-۲۶ | `v0.16.2` → `a38ba54` | MIT |
| [Holehe](https://github.com/megadose/holehe) | 15.2k | **هیچ تگی ندارد** | ۲۰۲۴-۰۹-۱۰ | کامیت `14da70f` | GPL-3.0 |

روش بررسی: تگ‌ها با `git ls-remote --tags`، تاریخ‌ها با `git log -1` روی کلون واقعی، ستاره‌ها از صفحهٔ گیت‌هاب هر پروژه.
بخش Releases در صفحهٔ گیت‌هاب هر سه پروژه خالی نمایش داده شد؛ برای همین «آخرین نسخه» بر اساس **تگ‌ها** است.

> ⚠️ **اصلاح مجوز SpiderFoot:** شما نوشته بودید SpiderFoot مجوز MIT دارد. این برای شاخهٔ `master` درست است
> (کامیت `9aa6ec3` در ۲۰۲۲-۰۵-۰۶ با پیام *Update the license from GPL to MIT*)،
> ولی تگ `v4.0` **یک ماه قبل از آن** ساخته شده و فایل `LICENSE` داخل همین تگ، **GNU GPL نسخهٔ 2** است.
> چون ما روی `v4.0` قفل کرده‌ایم، مجوز معتبر برای کدی که داریم GPL-2.0 است. می‌توانید خودتان بررسی کنید:
> `head -2 modules/spiderfoot/LICENSE`

---

## مرحلهٔ ۰ — اطمینان از اینکه WSL نسخهٔ 2 است

منبع: [Microsoft Learn — Basic commands for WSL](https://learn.microsoft.com/en-us/windows/wsl/basic-commands)

PowerShell را باز کنید (منوی Start → تایپ PowerShell) و بزنید:

```powershell
PS> wsl -l -v
```

**چه می‌کند:** فهرست توزیع‌های لینوکس نصب‌شده را با نسخهٔ WSL هرکدام نشان می‌دهد.
**خروجی مورد انتظار:** چیزی شبیه جدول زیر؛ مهم ستون `VERSION` است که باید **2** باشد. (نام دقیق توزیع ممکن است فرق کند.)

```
  NAME      STATE           VERSION
* Ubuntu    Running         2
```

اگر `1` بود، با نامی که در ستون NAME دیدید تبدیلش کنید (طبق همان صفحهٔ مایکروسافت):

```powershell
PS> wsl --set-version Ubuntu 2
```

---

## مرحلهٔ ۱ — پیش‌نیازها

### ۱-۱. به‌روزرسانی فهرست بسته‌ها و نصب git و curl

منبع: [git-scm.com — Installing Git (Linux)](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)

```bash
sudo apt update
```

**چه می‌کند:** فهرست بسته‌های موجود را از مخازن اوبونتو دوباره می‌خواند (چیزی نصب نمی‌کند). رمز کاربر لینوکس را می‌پرسد؛ هنگام تایپ رمز چیزی نمایش داده نمی‌شود و این عادی است.
**خروجی مورد انتظار:** چند خط `Hit:` یا `Get:` و در پایان `Reading package lists... Done`.

```bash
sudo apt install -y git curl
```

**چه می‌کند:** git (مدیریت نسخه) و curl (دانلود از اینترنت) را نصب می‌کند. `-y` یعنی «بله» را خودکار بزن.
**خروجی مورد انتظار:** یا مراحل نصب، یا اگر قبلاً نصب باشند: `git is already the newest version`.

```bash
git --version
```

**خروجی مورد انتظار:** `git version 2.x.y` (عدد دقیق به نسخهٔ اوبونتو بستگی دارد).

### ۱-۲. معرفی خودتان به git

منبع: [git-scm.com — First-Time Git Setup](https://git-scm.com/book/en/v2/Getting-Started-First-Time-Git-Setup)

این دو دستور را **با نام و ایمیل خودتان** اجرا کنید (متن داخل گیومه را عوض کنید). این نام و ایمیل روی هر کامیت ثبت و در گیت‌هاب **عمومی** دیده می‌شود.
اگر نمی‌خواهید ایمیل اصلی‌تان عمومی شود، از ایمیل `noreply` گیت‌هاب استفاده کنید ([راهنمای گیت‌هاب](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address)) که در Settings → Emails گیت‌هاب نمایش داده می‌شود.

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
git config --global init.defaultBranch main
```

**چه می‌کند:** تنظیمات را در فایل `~/.gitconfig` می‌نویسد. خط سوم باعث می‌شود مخزن‌های جدید به‌طور پیش‌فرض شاخهٔ `main` داشته باشند.
**خروجی مورد انتظار:** هیچ (سکوت یعنی موفقیت). برای بررسی:

```bash
git config --global --list
```

### ۱-۳. نصب uv با نصب‌کنندهٔ رسمی

منبع: [docs.astral.sh/uv — Installation](https://docs.astral.sh/uv/getting-started/installation/)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**چه می‌کند:** اسکریپت نصب رسمی uv را دانلود و اجرا می‌کند. uv را در `~/.local/bin` می‌گذارد و **به پایتون سیستم دست نمی‌زند**.
**خروجی مورد انتظار:** پیام‌هایی مثل `installing to /home/<user>/.local/bin` و در آخر `everything's installed!`.

برای اینکه ترمینال فعلی uv را بشناسد (یا ترمینال را ببندید و دوباره باز کنید):

```bash
source $HOME/.local/bin/env
uv --version
```

**خروجی مورد انتظار:** `uv 0.x.y` (در ساخت این مخزن: `uv 0.11.32`).

### ۱-۴. نصب Python 3.12 جداگانه با uv

منبع: [docs.astral.sh/uv — Installing Python](https://docs.astral.sh/uv/guides/install-python/)

```bash
uv python install 3.12
```

**چه می‌کند:** یک پایتون 3.12 مستقل در `~/.local/share/uv/python/` دانلود می‌کند. پایتون 3.14 سیستم شما **دست نمی‌خورد**.
**خروجی مورد انتظار:** `Installed Python 3.12.x in ...` (اگر از قبل باشد: `Python 3.12 is already installed`).

```bash
uv python list
```

**چه می‌کند:** همهٔ پایتون‌هایی که uv می‌بیند را نشان می‌دهد.
**خروجی واقعی (بخشی از آن):**

```
cpython-3.12.13-linux-x86_64-gnu   /root/.local/share/uv/python/cpython-3.12-linux-x86_64-gnu/bin/python3.12
```

خطی که مسیرش داخل `.local/share/uv/python` است، همان پایتونی است که uv نصب کرده. پایتون سیستم شما (3.14) با مسیر `/usr/bin/...` نمایش داده می‌شود.

**چرا 3.12؟** (بررسی‌شده) SpiderFoot در `requirements.txt` خود `lxml<5` را می‌خواهد و lxml 4.9.4 حداکثر برای CPython 3.12 فایل wheel آماده دارد. Sherlock در `pyproject.toml` نسخه‌های 3.10 تا 3.13 را رسماً فهرست کرده است.

---

## مرحلهٔ ۲ — احراز هویت در گیت‌هاب با کلید SSH

منبع: [GitHub Docs — Generating a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)،
[Adding a new SSH key to your account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)،
[Testing your SSH connection](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/testing-your-ssh-connection)

گیت‌هاب برای عملیات git دیگر **رمز عبور حساب** را قبول نمی‌کند؛ باید SSH یا Personal Access Token داشته باشید.

### ۲-۱. ساخت کلید

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

**چه می‌کند:** یک جفت کلید می‌سازد: خصوصی (`~/.ssh/id_ed25519` — هرگز به کسی ندهید) و عمومی (`~/.ssh/id_ed25519.pub`).
**چه می‌پرسد:** مسیر ذخیره (فقط Enter بزنید) و یک passphrase (رمز برای خود کلید؛ توصیه می‌شود بگذارید).
**خروجی مورد انتظار:** `Your identification has been saved in ...` و یک تصویر ASCII به نام randomart.

### ۲-۲. اضافه کردن کلید به ssh-agent

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**خروجی مورد انتظار:** `Agent pid 12345` و بعد `Identity added: /home/<user>/.ssh/id_ed25519 (...)`.

### ۲-۳. دادن کلید عمومی به گیت‌هاب

```bash
cat ~/.ssh/id_ed25519.pub
```

خروجی یک خط است که با `ssh-ed25519 ` شروع می‌شود. **کل خط** را کپی کنید.
در گیت‌هاب: عکس پروفایل → **Settings** → **SSH and GPG keys** → **New SSH key** → یک Title دلخواه، Key type: `Authentication Key`، خط را در Key بچسبانید → **Add SSH key**.

### ۲-۴. آزمایش اتصال

```bash
ssh -T git@github.com
```

**بار اول** می‌پرسد آیا به سرور اعتماد دارید و یک fingerprint نشان می‌دهد. آن را با فهرست رسمی
[GitHub's SSH key fingerprints](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints)
مقایسه کنید (برای ED25519: `SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`) و اگر یکی بود `yes` بنویسید.

**خروجی مورد انتظار در صورت موفقیت:**

```
Hi amirxoo13! You've successfully authenticated, but GitHub does not provide shell access.
```

(این پیام «shell access ندارید» خطا نیست؛ یعنی موفق شدید.)

**جایگزین (PAT):** اگر نخواستید SSH، از
[Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
یک توکن بسازید و هنگام push به‌جای رمز وارد کنید. در این راهنما با SSH ادامه می‌دهیم.

---

## مرحلهٔ ۳ — ساخت پروژه و اضافه کردن submoduleها

منبع: [git-scm.com — Git Tools: Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)، [git-submodule](https://git-scm.com/docs/git-submodule)
دربارهٔ اینکه چرا داخل `~` و نه `/mnt/c`: [Microsoft Learn — Working across file systems](https://learn.microsoft.com/en-us/windows/wsl/filesystems) (برای بهترین سرعت، فایل‌ها را در فایل‌سیستم لینوکس نگه دارید).

> ℹ️ **توجه دربارهٔ وضعیت فعلی مخزن روی گیت‌هاب:** من همین ساختار را ساخته، آزمایش و در شاخهٔ
> `claude/email-osint-setup-pmzjwr` push کرده‌ام. چون مخزن خالی بود، گیت‌هاب **همان شاخه را شاخهٔ پیش‌فرض**
> قرار داده است. شما دو راه دارید که در **مرحلهٔ ۵** توضیح داده‌ام. اگر می‌خواهید یاد بگیرید، مراحل ۳ تا ۵ را خودتان از صفر انجام دهید.

### ۳-۱. ساخت پوشه و مخزن

```bash
cd ~
mkdir ~/Email-OSINT- && cd ~/Email-OSINT- && git init -b main
```

**چه می‌کند:** پوشه را در خانهٔ لینوکس می‌سازد، واردش می‌شود و یک مخزن git خالی با شاخهٔ `main` می‌سازد.
**خروجی مورد انتظار:** `Initialized empty Git repository in /home/<user>/Email-OSINT-/.git/`
(اگر پوشه از قبل وجود داشته باشد `mkdir` خطای `File exists` می‌دهد و بقیه اجرا نمی‌شود.)

### ۳-۲. اضافه کردن سه submodule

```bash
git submodule add https://github.com/smicallef/spiderfoot.git modules/spiderfoot
git submodule add https://github.com/sherlock-project/sherlock.git modules/sherlock
git submodule add https://github.com/megadose/holehe.git modules/holehe
```

**چه می‌کند:** هر پروژه را در مسیر داده‌شده کلون می‌کند و آدرس و مسیرش را **خودکار** در فایل `.gitmodules` می‌نویسد (این فایل را دستی نسازید).
از آدرس HTTPS استفاده کرده‌ایم تا هرکس مخزن را کلون می‌کند، بدون کلید SSH هم بتواند submoduleها را بگیرد.
**خروجی واقعی:** برای هرکدام `Cloning into '/home/<user>/Email-OSINT-/modules/spiderfoot'...` و نوار پیشرفت.

### ۳-۳. قفل کردن هر submodule روی نسخهٔ مشخص

```bash
git -C modules/spiderfoot checkout v4.0
git -C modules/sherlock checkout v0.16.2
git -C modules/holehe checkout 14da70f588538936b20d238783c5e28a0772a2b3
```

**چه می‌کند:** `git -C <مسیر>` یعنی «این دستور را انگار داخل آن پوشه اجرا کن». هر submodule را روی تگ/کامیت مشخص می‌برد.
Holehe هیچ تگی ندارد (`git ls-remote --tags` خروجی خالی داد)، پس روی آخرین کامیت master قفل شده است.
**خروجی مورد انتظار:** پیامی که با `Note: switching to 'v4.0'.` شروع می‌شود و می‌گوید در حالت **`detached HEAD`** هستید.
این برای submodule **کاملاً عادی و مطلوب** است: یعنی روی یک کامیت ثابت ایستاده‌اید نه روی شاخه‌ای که جلو می‌رود.

### ۳-۴. ثبت (stage) اشاره‌گر submoduleها

```bash
git add modules/spiderfoot modules/sherlock modules/holehe
```

**چه می‌کند:** مخزن اصلی، محتوای فایل‌های submodule را ذخیره نمی‌کند؛ فقط **شناسهٔ کامیتی** که هر submodule رویش ایستاده را ذخیره می‌کند. این دستور آن شناسه‌ها را برای کامیت آماده می‌کند.
**خروجی مورد انتظار:** هیچ.

### ۳-۵. همگام‌سازی

```bash
git submodule update --init --recursive
```

**چه می‌کند:** مطمئن می‌شود هر submodule مقداردهی شده و روی همان کامیتی است که مخزن اصلی ثبت کرده (و اگر submoduleها خودشان submodule داشتند، آن‌ها را هم می‌گیرد).
**خروجی مورد انتظار:** اینجا معمولاً هیچ، چون همه‌چیز از قبل درست است.

### ۳-۶. بررسی و توضیح خروجی‌ها

```bash
cat .gitmodules
```

**خروجی واقعی:**

```
[submodule "modules/spiderfoot"]
	path = modules/spiderfoot
	url = https://github.com/smicallef/spiderfoot.git
[submodule "modules/sherlock"]
	path = modules/sherlock
	url = https://github.com/sherlock-project/sherlock.git
[submodule "modules/holehe"]
	path = modules/holehe
	url = https://github.com/megadose/holehe.git
```

- `[submodule "..."]` نام submodule است.
- `path` جایی است که داخل مخزن قرار می‌گیرد.
- `url` آدرسی است که git هنگام کلون از آن می‌گیرد.
- **نکته:** نسخه/تگ در این فایل نیست! نسخه در خودِ کامیت مخزن اصلی ذخیره می‌شود (مرحلهٔ ۳-۴).

```bash
git submodule status
```

**خروجی واقعی:**

```
 14da70f588538936b20d238783c5e28a0772a2b3 modules/holehe (heads/master)
 a38ba54fda799cd786a2ab67a50143e1a63169e6 modules/sherlock (v0.16.0-288-ga38ba54)
 b9c345de5b085debc7444fc10e0e26e7745df5f2 modules/spiderfoot (v2.11.0-final-2860-gb9c345de)
```

توضیح هر بخش (طبق [مستند git-submodule](https://git-scm.com/docs/git-submodule#Documentation/git-submodule.txt-status--cached--recursive--ltpathgt82308203)):

- **کاراکتر اول:** فاصله = همه‌چیز درست است. `-` = submodule مقداردهی نشده (پوشه خالی). `+` = کامیتی که submodule رویش است با کامیتی که مخزن اصلی ثبت کرده فرق دارد. `U` = تعارض merge.
- **عدد ۴۰ رقمی:** شناسهٔ کامیتی که submodule رویش ایستاده.
- **داخل پرانتز:** خروجی `git describe` برای آن کامیت. چون تگ‌های `v4.0` و `v0.16.2` از نوع «سبک» (lightweight) هستند، `git describe` معمولی آن‌ها را نادیده می‌گیرد و به یک تگ قدیمی‌تر annotated اشاره می‌کند؛ این **اشتباه نیست**. برای دیدن تگ واقعی:

```bash
git -C modules/sherlock describe --tags
git -C modules/spiderfoot describe --tags
```

**خروجی واقعی:** `v0.16.2` و `v4.0`.

---

## مرحلهٔ ۴ — فایل‌های ریشه

سه فایل در ریشه لازم است. محتوای واقعی آن‌ها در همین مخزن هست و می‌توانید عیناً کپی کنید:

- `README.md` — هدف، ساختار، مجوزها و تذکر حقوقی/اخلاقی.
- `.gitignore` — نادیده گرفتن `venvs/`، `__pycache__/` و خروجی اسکن‌ها (`output/`، `results/`، `reports/`، `*.csv`، `*.xlsx`).
- `setup.sh` و `build-constraints.txt` — در مرحلهٔ ۸ توضیح داده شده‌اند.

ساده‌ترین راه کپی (اگر شاخهٔ من روی گیت‌هاب هست):

```bash
cd ~/Email-OSINT-
for f in README.md .gitignore setup.sh build-constraints.txt docs/GUIDE.fa.md; do
  mkdir -p "$(dirname "$f")"
  curl -fsSL "https://raw.githubusercontent.com/amirxoo13/Email-OSINT-/claude/email-osint-setup-pmzjwr/$f" -o "$f"
done
ls -la
```

**چه می‌کند:** هر فایل را از شاخهٔ من دانلود می‌کند. `-f` باعث می‌شود اگر فایل پیدا نشد، خطا بدهد به‌جای ذخیرهٔ صفحهٔ خطا.
**خروجی مورد انتظار:** در `ls -la` این فایل‌ها را می‌بینید.

---

## مرحلهٔ ۵ — کامیت و push

منبع: [git-scm.com — Working with Remotes](https://git-scm.com/book/en/v2/Git-Basics-Working-with-Remotes)، [GitHub Docs — Managing remote repositories](https://docs.github.com/en/get-started/getting-started-with-git/managing-remote-repositories)

```bash
git add .
git status
```

**خروجی مورد انتظار:** در بخش `Changes to be committed` باید `.gitmodules`، `modules/holehe`، `modules/sherlock`، `modules/spiderfoot` و فایل‌های ریشه را ببینید. **نباید** `venvs/` را ببینید (به لطف `.gitignore`).

```bash
git commit -m "Add SpiderFoot, Sherlock and Holehe as pinned submodules"
```

**خروجی مورد انتظار:** `[main (root-commit) xxxxxxx] Add ...` و تعداد فایل‌ها. سه خط `create mode 160000 modules/...` یعنی ثبت submodule (عدد 160000 نوع ویژهٔ «gitlink» است).

```bash
git remote add origin git@github.com:amirxoo13/Email-OSINT-.git
git remote -v
```

**چه می‌کند:** آدرس SSH مخزن گیت‌هاب را با نام `origin` ثبت می‌کند. (خط تیرهٔ آخر اسم مخزن جزو اسم است.)
**خروجی مورد انتظار:** دو خط `origin  git@github.com:amirxoo13/Email-OSINT-.git (fetch)` و `(push)`.

```bash
git push -u origin main
```

**چه می‌کند:** شاخهٔ `main` را به گیت‌هاب می‌فرستد و `-u` آن را به‌عنوان شاخهٔ ردیابی تنظیم می‌کند تا بعداً فقط `git push` کافی باشد.
**خروجی مورد انتظار:** `Writing objects: 100% ...` و `* [new branch]      main -> main` و `branch 'main' set up to track 'origin/main'.`

### تنظیم `main` به‌عنوان شاخهٔ پیش‌فرض

چون شاخهٔ من زودتر push شده، گیت‌هاب آن را پیش‌فرض گذاشته است. طبق
[Changing the default branch](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-branches-in-your-repository/changing-the-default-branch):
صفحهٔ مخزن → **Settings** → بخش **Default branch** → آیکون دو فلش → `main` را انتخاب → **Update**.
بعد از آن اگر خواستید شاخهٔ `claude/email-osint-setup-pmzjwr` را از صفحهٔ **Branches** حذف کنید.

**راه دوم (بدون انجام مراحل ۳ تا ۵ از صفر):** کار من را بگیرید و به‌عنوان `main` بفرستید:

```bash
cd ~
git clone --recurse-submodules -b claude/email-osint-setup-pmzjwr git@github.com:amirxoo13/Email-OSINT-.git
cd Email-OSINT-
git push origin HEAD:main
```

سپس مانند بالا `main` را پیش‌فرض کنید و با `git switch main` (بعد از `git fetch origin`) روی آن کار کنید.

### بررسی در گیت‌هاب

صفحهٔ https://github.com/amirxoo13/Email-OSINT- را باز کنید و وارد پوشهٔ `modules` شوید. هر submodule به شکل
`spiderfoot @ b9c345d`، `sherlock @ a38ba54`، `holehe @ 14da70f` نمایش داده می‌شود؛ کلیک روی آن، شما را به **همان کامیت** در مخزن اصلی ابزار می‌برد.

---

## مرحلهٔ ۶ — کلون کردن روی سیستم دیگر

منبع: [git-scm.com — Cloning a Project with Submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

```bash
git clone --recurse-submodules https://github.com/amirxoo13/Email-OSINT-.git
```

**چه می‌کند:** مخزن اصلی و هر سه submodule را روی همان کامیت‌های قفل‌شده می‌گیرد.

اگر کسی **بدون** `--recurse-submodules` کلون کرده باشد، پوشه‌های `modules/*` خالی‌اند و `git submodule status` جلوی هرکدام `-` نشان می‌دهد. راه‌حل:

```bash
cd Email-OSINT-
git submodule update --init --recursive
```

---

## مرحلهٔ ۷ — به‌روزرسانی بعدی یک submodule (امن)

منبع: [git-scm.com — Pulling in Upstream Changes from the Submodule Remote](https://git-scm.com/book/en/v2/Git-Tools-Submodules)

مثال برای Sherlock:

```bash
cd ~/Email-OSINT-
git -C modules/sherlock fetch --tags
git -C modules/sherlock tag --sort=-creatordate | head -5
```

**چه می‌کند:** تگ‌های جدید را از گیت‌هاب می‌گیرد و ۵ تگ جدیدتر را نشان می‌دهد. فرض کنید تگ جدیدی دیدید؛ آن را جایگزین `<NEW_TAG>` کنید (این یک جای‌خالی است که **باید خودتان پر کنید**):

```bash
git -C modules/sherlock checkout <NEW_TAG>
git diff --submodule
```

`git diff --submodule` فهرست کامیت‌های بین نسخهٔ قبلی و جدید را نشان می‌دهد تا ببینید چه چیزی عوض شده.
سپس **اول آزمایش کنید** (`./setup.sh` و بعد `sherlock --help`)، و اگر همه‌چیز درست بود:

```bash
git add modules/sherlock
git commit -m "Bump sherlock to <NEW_TAG>"
git push
```

اگر خراب شد، برگشت ساده است: `git -C modules/sherlock checkout v0.16.2`.

**دیگران** بعد از `git pull` باید اجرا کنند: `git submodule update --init --recursive` (و دوباره `./setup.sh`).

### `git submodule update --remote` چه می‌کند؟

طبق [مستند git-submodule](https://git-scm.com/docs/git-submodule)، این دستور به‌جای کامیت ثبت‌شده در مخزن اصلی،
هر submodule را به **آخرین کامیت شاخهٔ ریموت** آن می‌برد (شاخه‌ای که با `branch` در `.gitmodules` تعیین شده، وگرنه شاخهٔ پیش‌فرض ریموت).
یعنی **قفل نسخه را کنار می‌گذارد** و شما را مثلاً به master جدید SpiderFoot می‌برد (که README خودش توصیه نمی‌کند). برای این پروژه از آن استفاده نکنید؛ روش تگ‌به‌تگ بالا امن‌تر است.

---

## مرحلهٔ ۸ — وابستگی‌ها: یک محیط مجازی برای هر ابزار

منابع: [uv — Using environments](https://docs.astral.sh/uv/pip/environments/)، [uv pip install (CLI reference)](https://docs.astral.sh/uv/reference/cli/#uv-pip-install)،
[README رسمی SpiderFoot](https://github.com/smicallef/spiderfoot#installing--running)، [README رسمی Sherlock](https://github.com/sherlock-project/sherlock#installation)، [README رسمی Holehe](https://github.com/megadose/holehe#%EF%B8%8F-installation)

چرا جدا؟ SpiderFoot نسخه‌های خیلی قدیمی (مثلاً `cryptography<4`، `pyyaml<6`، `lxml<5`) می‌خواهد که با وابستگی‌های دو ابزار دیگر تداخل پیدا می‌کنند. یک `requirements.txt` ادغام‌شده نمی‌سازیم.

### آنچه اسکریپت انجام می‌دهد

| venv | دستور نصب | مبنای رسمی |
|---|---|---|
| `venvs/sherlock` | `uv pip install modules/sherlock` | README شرلوک: نصب با pipx/pip/uv؛ پوشهٔ آن یک `pyproject.toml` استاندارد دارد |
| `venvs/holehe` | `uv pip install modules/holehe` | README هولهه نصب از گیت‌هاب را با `python3 setup.py install` می‌گوید؛ این روش در setuptools منسوخ شده و نصب همان پوشه با pip/uv معادل امروزی آن است |
| `venvs/spiderfoot` | `uv pip install -b build-constraints.txt -r modules/spiderfoot/requirements.txt` | README اسپایدرفوت: `pip3 install -r requirements.txt` |

### مشکل واقعی که پیدا شد و راه‌حلش

اجرای ساده `uv pip install -r modules/spiderfoot/requirements.txt` با پایتون 3.12 **شکست خورد**. خروجی واقعی:

```
   Building pyyaml==5.4.1
  × Failed to build `pyyaml==5.4.1`
  ├─▶ The build backend returned an error
  ╰─▶ Call to `setuptools.build_meta.build_wheel` failed (exit status: 1)
...
      AttributeError: 'build_ext' object has no attribute 'cython_sources'
```

**چطور خطا را بخوانیم:** (۱) دنبال خط `Failed to build` بگردید تا بفهمید **کدام بسته** شکست خورد (اینجا `pyyaml==5.4.1`).
(۲) آخرین خط traceback علت را می‌گوید (اینجا `cython_sources`). (۳) با جست‌وجوی همین پیام، به
[issue رسمی PyYAML شمارهٔ 724](https://github.com/yaml/pyyaml/issues/724) می‌رسید: PyYAML 5.4.1 با **Cython 3** ساخته نمی‌شود.
SpiderFoot `pyyaml<6` می‌خواهد و 5.4.1 برای پایتون 3.12 فایل آماده (wheel) ندارد، پس باید از سورس ساخته شود.

**راه‌حل:** گزینهٔ رسمی uv به نام `--build-constraints` (یا `-b`) فقط برای **زمان ساخت** محدودیت می‌گذارد. فایل `build-constraints.txt` شامل `cython<3` است. با آن، نصب کامل شد (۶۰ بسته، از جمله `lxml==4.9.4`، `pyyaml==5.4.1`، `cryptography==3.4.8`).

### اجرای اسکریپت

```bash
cd ~/Email-OSINT-
chmod +x setup.sh
./setup.sh
```

**چه می‌کند:** `chmod +x` فایل را «قابل اجرا» می‌کند (فقط یک‌بار لازم است). `./setup.sh` آن را اجرا می‌کند.
اسکریپت با `set -euo pipefail` شروع می‌شود؛ یعنی **با اولین خطا متوقف می‌شود** و ادامه نمی‌دهد.
قبل از شروع بررسی می‌کند که uv نصب باشد و پوشه‌های submodule خالی نباشند.
**خروجی واقعی (خلاصه):**

```
[*] Making sure Python 3.12 is available to uv
Python 3.12 is already installed
[*] Creating venvs/sherlock (Python 3.12)
Python 3.12.13
[*] Installing Sherlock from modules/sherlock
 + sherlock-project==0.16.2 (from file:///.../modules/sherlock)
[+] Sherlock installed
[*] Creating venvs/holehe (Python 3.12)
Python 3.12.13
[+] Holehe installed
[*] Creating venvs/spiderfoot (Python 3.12)
Python 3.12.13
   Building pyyaml==5.4.1
[+] SpiderFoot requirements installed
[*] Done. Activate a tool's venv before using it, for example:
```

اجرای دوباره اسکریپت امن است (`uv venv --clear` محیط را از نو می‌سازد).

### راه جایگزین برای SpiderFoot: Docker (آزمایش نشده)

اگر نصب پایتونی SpiderFoot روی سیستم شما باز هم شکست خورد، فایل‌های رسمی Docker داخل `modules/spiderfoot` هستند.
نیاز به Docker دارید ([Docker Desktop با WSL 2](https://docs.docker.com/desktop/features/wsl/)).
طبق توضیحات داخل همان `docker-compose.yml`:

```bash
cd ~/Email-OSINT-/modules/spiderfoot
docker compose up
```

یا طبق توضیحات داخل `Dockerfile`:

```bash
docker build -t spiderfoot .
docker run -p 5001:5001 --security-opt no-new-privileges spiderfoot
```

⚠️ **این مسیر را من در این محیط آزمایش نکرده‌ام** (Docker در محیط من نبود). Dockerfile این نسخه بر پایهٔ Alpine 3.12/3.13 (قدیمی) است و ممکن است امروز در ساخت به مشکل بخورد.

---

## مرحلهٔ ۹ — آزمایش دود (Smoke test)

هر بار قبل از استفاده، venv همان ابزار را **فعال** کنید. بعد از فعال‌سازی، اول خط ترمینال `(sherlock)` یا مشابه نمایش داده می‌شود. `deactivate` آن را غیرفعال می‌کند.

### Sherlock

```bash
cd ~/Email-OSINT-
source venvs/sherlock/bin/activate
python --version
sherlock --help
deactivate
```

**خروجی واقعی:**

```
Python 3.12.13
usage: sherlock [-h] [--version] [--verbose] [--folderoutput FOLDEROUTPUT]
                [--output OUTPUT] [--csv] [--xlsx] [--site SITE_NAME]
                [--proxy PROXY_URL] [--dump-response] [--json JSON_FILE]
                [--timeout TIMEOUT] [--print-all] [--print-found] [--no-color]
                [--browse] [--local] [--nsfw] [--txt] [--ignore-exclusions]
                USERNAMES [USERNAMES ...]

Sherlock: Find Usernames Across Social Networks (Version 0.16.2)
```

### Holehe

```bash
source venvs/holehe/bin/activate
python --version
holehe --help
deactivate
```

**خروجی واقعی (ابتدای آن):**

```
Python 3.12.13
usage: holehe [-h] [--only-used] [--no-color] [--no-clear] [-NP] [-C]
              [-T TIMEOUT]
              EMAIL [EMAIL ...]

holehe v1.61
```

### SpiderFoot

```bash
source venvs/spiderfoot/bin/activate
cd modules/spiderfoot
python sf.py -l 127.0.0.1:5001
```

**چه می‌کند:** وب‌سرور SpiderFoot را روی پورت 5001 بالا می‌آورد. ترمینال مشغول می‌ماند؛ برای توقف `Ctrl+C` بزنید.
**خروجی واقعی:** ابتدا تعدادی `SyntaxWarning: invalid escape sequence` از کتابخانه‌های قدیمی `adblockparser` و `ipwhois` می‌آید —
این‌ها **هشدارند نه خطا** (پایتون 3.12 دربارهٔ کد قدیمی هشدار می‌دهد) و مانع اجرا نیستند. سپس:

```
*************************************************************
 Use SpiderFoot by starting your web browser of choice and
 browse to http://127.0.0.1:5001/
*************************************************************

[INFO] sf : Starting web server at 127.0.0.1:5001 ...
[WARNING] sf :
Warning: passwd file contains no passwords. Authentication disabled.
```

حالا در **مرورگر ویندوز** به آدرس http://127.0.0.1:5001 بروید. عنوان صفحه `SpiderFoot v4.0.0` است
(این را در محیط من با `curl` بررسی کردم: کد پاسخ `200`). WSL 2 به‌طور پیش‌فرض `localhost` را به ویندوز فوروارد می‌کند
([Microsoft Learn — Accessing network applications with WSL](https://learn.microsoft.com/en-us/windows/wsl/networking)).
پایگاه داده و لاگ‌ها در `~/.spiderfoot/` ذخیره می‌شوند، نه داخل مخزن.

---

## مرحلهٔ ۱۰ — عیب‌یابی

| مشکل | علامت | راه‌حل |
|---|---|---|
| **احراز هویت / push رد شد** | `Permission denied (publickey)` | `ssh -T git@github.com` را بزنید. اگر همین خطا بود، کلید در گیت‌هاب ثبت نشده یا agent آن را ندارد: `ssh-add ~/.ssh/id_ed25519`. ([Error: Permission denied (publickey)](https://docs.github.com/en/authentication/troubleshooting-ssh/error-permission-denied-publickey)) |
| | `Support for password authentication was removed` | remote روی HTTPS است و رمز حساب را داده‌اید. به SSH تغییر دهید: `git remote set-url origin git@github.com:amirxoo13/Email-OSINT-.git` |
| | `! [rejected] main -> main (fetch first)` | روی گیت‌هاب کامیتی هست که شما ندارید. `git pull origin main` و بعد دوباره `git push`. |
| **پوشهٔ submodule خالی** | `ls modules/sherlock` چیزی نشان نمی‌دهد؛ `git submodule status` با `-` | `git submodule update --init --recursive` |
| **detached HEAD در submodule** | `git -C modules/sherlock status` می‌گوید `HEAD detached at v0.16.2` | **عادی است.** submodule باید روی یک کامیت ثابت باشد. فقط اگر بخواهید داخل خود ابزار تغییر بدهید یک شاخه بسازید (`git -C modules/sherlock switch -c my-change`). |
| | `git submodule status` با `+` | submodule از کامیت ثبت‌شده جابه‌جا شده. برگرداندن: `git submodule update --init --recursive`؛ یا اگر عمدی بوده: `git add modules/<tool>` و کامیت. |
| **خطای ساخت uv/pip** | `Failed to build <package>` | خط `Failed to build` را برای نام بسته و آخرین خط traceback را برای علت بخوانید. اگر بستهٔ C دارد (مثل lxml)، ممکن است ابزار کامپایل لازم باشد: `sudo apt install -y build-essential python3-dev libxml2-dev libxslt1-dev`. نمونهٔ واقعی pyyaml در مرحلهٔ ۸ آمده. |
| | `externally-managed-environment` | شما با `pip` پایتون سیستم نصب کرده‌اید. هرگز این کار را نکنید؛ همیشه از venvها یا `./setup.sh` استفاده کنید. |
| **نسخهٔ اشتباه پایتون در venv** | `python --version` بعد از activate چیزی جز 3.12 نشان می‌دهد | venv را پاک کرده و از نو بسازید: `rm -rf venvs/<tool>` و دوباره `./setup.sh`. اطمینان از وجود 3.12: `uv python list`. |
| | `command not found: sherlock` | venv فعال نیست: `source venvs/sherlock/bin/activate`. |
| **uv پیدا نمی‌شود** | `uv: command not found` | `source $HOME/.local/bin/env` یا ترمینال را بسته و باز کنید. |
| **صفحهٔ SpiderFoot باز نمی‌شود** | مرورگر ویندوز وصل نمی‌شود | مطمئن شوید ترمینال SpiderFoot هنوز باز است و خطای `Address already in use` نداده؛ در غیر این صورت پورت دیگری بدهید: `python sf.py -l 127.0.0.1:5002`. |

---

## تذکر حقوقی و اخلاقی

این ابزارها از سایت‌ها و سرویس‌های دیگران اطلاعات می‌پرسند. فقط روی اطلاعات خودتان یا با **مجوز صریح و کتبی** صاحب اطلاعات (مثل تست نفوذ مجاز) استفاده کنید،
قوانین کشور خودتان و کشور هدف و شرایط استفادهٔ سایت‌ها را رعایت کنید، و هرگز برای تعقیب، آزار یا افشای اطلاعات افراد به کار نبرید. مسئولیت استفاده با خودتان است.

</div>
