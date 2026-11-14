.class public Lcom/holy/dash/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.java"


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/holy/dash/MainActivity$Bridge;,
        Lcom/holy/dash/MainActivity$Client;,
        Lcom/holy/dash/MainActivity$Chrome;
    }
.end annotation


# static fields
.field static final LOCK_GRACE_MS:J = 0x7530L

.field static final REQ_FILE:I = 0xd

.field static final REQ_LOCK:I = 0xe

.field static final REQ_NOTIF:I = 0xb

.field static final REQ_STORAGE:I = 0xc

.field static unlockedAt:J


# instance fields
.field authBusy:Z

.field bar:Landroid/widget/ProgressBar;

.field bg:I

.field bioBusy:Z

.field clipTried:Z

.field cutTop:I

.field err:Landroid/view/View;

.field errShown:Z

.field errText:Landroid/widget/TextView;

.field fileCb:Landroid/webkit/ValueCallback;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Landroid/webkit/ValueCallback",
            "<[",
            "Landroid/net/Uri;",
            ">;"
        }
    .end annotation
.end field

.field imeOld:I

.field lastBack:J

.field lockMsg:Landroid/widget/TextView;

.field lockView:Landroid/view/View;

.field oldWarned:Z

.field volatile origin:Ljava/lang/String;

.field volatile pageOrigin:Ljava/lang/String;

.field pageReady:Z

.field pendingGo:Ljava/lang/String;

.field pendingLock:Ljava/lang/Boolean;

.field pendingSave:[B

.field pendingSaveMime:Ljava/lang/String;

.field pendingSaveName:Ljava/lang/String;

.field pendingWeb:Z

.field final retry:Ljava/lang/Runnable;

.field root:Landroid/widget/FrameLayout;

.field setup:Landroid/view/View;

.field setupMsg:Landroid/widget/TextView;

.field stoppedAt:J

.field final ui:Landroid/os/Handler;

.field urlField:Landroid/widget/EditText;

.field web:Landroid/webkit/WebView;


# direct methods
.method static constructor <clinit>()V
    .registers 2

    .prologue
    .line 80
    const-wide/16 v0, 0x0

    sput-wide v0, Lcom/holy/dash/MainActivity;->unlockedAt:J

    return-void
.end method

.method public constructor <init>()V
    .registers 3

    .prologue
    .line 77
    invoke-direct {p0}, Landroid/app/Activity;-><init>()V

    .line 83
    new-instance v0, Landroid/os/Handler;

    invoke-static {}, Landroid/os/Looper;->getMainLooper()Landroid/os/Looper;

    move-result-object v1

    invoke-direct {v0, v1}, Landroid/os/Handler;-><init>(Landroid/os/Looper;)V

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    .line 91
    const-string v0, ""

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    .line 92
    const-string v0, ""

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->pageOrigin:Ljava/lang/String;

    .line 97
    const-wide/16 v0, 0x0

    iput-wide v0, p0, Lcom/holy/dash/MainActivity;->stoppedAt:J

    .line 106
    new-instance v0, Lcom/holy/dash/MainActivity$1;

    invoke-direct {v0, p0}, Lcom/holy/dash/MainActivity$1;-><init>(Lcom/holy/dash/MainActivity;)V

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->retry:Ljava/lang/Runnable;

    return-void
.end method

.method static parseCssColor(Ljava/lang/String;)I
    .registers 5

    .prologue
    .line 1037
    :try_start_0
    const-string v0, "rgba?\\((\\d+)\\D+(\\d+)\\D+(\\d+)"

    invoke-static {v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v0

    .line 1038
    invoke-virtual {v0}, Ljava/util/regex/Matcher;->find()Z

    move-result v1

    if-eqz v1, :cond_30

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Ljava/util/regex/Matcher;->group(I)Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result v1

    const/4 v2, 0x2

    invoke-virtual {v0, v2}, Ljava/util/regex/Matcher;->group(I)Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result v2

    const/4 v3, 0x3

    invoke-virtual {v0, v3}, Ljava/util/regex/Matcher;->group(I)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I

    move-result v0

    invoke-static {v1, v2, v0}, Landroid/graphics/Color;->rgb(III)I

    move-result v0

    .line 1043
    :goto_2f
    return v0

    .line 1039
    :cond_30
    const-string v0, "#[0-9a-fA-F]{6}"

    invoke-virtual {p0, v0}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_3e

    invoke-static {p0}, Landroid/graphics/Color;->parseColor(Ljava/lang/String;)I
    :try_end_3b
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_3b} :catch_3d

    move-result v0

    goto :goto_2f

    .line 1040
    :catch_3d
    move-exception v0

    .line 1043
    :cond_3e
    const/4 v0, 0x0

    goto :goto_2f
.end method

.method static safeName(Ljava/lang/String;)Ljava/lang/String;
    .registers 4

    .prologue
    .line 981
    if-nez p0, :cond_38

    const-string v0, ""

    .line 982
    :goto_4
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-nez v1, :cond_12

    const-string v1, "."

    invoke-virtual {v0, v1}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v1

    if-eqz v1, :cond_25

    :cond_12
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "holy_file"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 983
    :cond_25
    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v1

    const/16 v2, 0x78

    if-le v1, v2, :cond_37

    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v1

    add-int/lit8 v1, v1, -0x78

    invoke-virtual {v0, v1}, Ljava/lang/String;->substring(I)Ljava/lang/String;

    move-result-object v0

    :cond_37
    return-object v0

    .line 981
    :cond_38
    const-string v0, "[\\\\/:*?\"<>|\\u0000-\\u001f]"

    const-string v1, "_"

    invoke-virtual {p0, v0, v1}, Ljava/lang/String;->replaceAll(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    goto :goto_4
.end method


# virtual methods
.method applyBg(I)V
    .registers 4

    .prologue
    .line 1047
    if-eqz p1, :cond_6

    iget v0, p0, Lcom/holy/dash/MainActivity;->bg:I

    if-ne p1, v0, :cond_7

    .line 1055
    :cond_6
    :goto_6
    return-void

    .line 1048
    :cond_7
    iput p1, p0, Lcom/holy/dash/MainActivity;->bg:I

    .line 1049
    invoke-static {p0, p1}, Lcom/holy/dash/Prefs;->setBg(Landroid/content/Context;I)V

    .line 1050
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    new-instance v1, Landroid/graphics/drawable/ColorDrawable;

    invoke-direct {v1, p1}, Landroid/graphics/drawable/ColorDrawable;-><init>(I)V

    invoke-virtual {v0, v1}, Landroid/view/Window;->setBackgroundDrawable(Landroid/graphics/drawable/Drawable;)V

    .line 1051
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0, p1}, Landroid/view/Window;->setStatusBarColor(I)V

    .line 1052
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0, p1}, Landroid/view/Window;->setNavigationBarColor(I)V

    .line 1053
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v0, p1}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    .line 1054
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_6

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0, p1}, Landroid/webkit/WebView;->setBackgroundColor(I)V

    goto :goto_6
.end method

.method applyOldPadding()V
    .registers 5

    .prologue
    const/4 v3, 0x0

    .line 241
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    iget v1, p0, Lcom/holy/dash/MainActivity;->cutTop:I

    iget v2, p0, Lcom/holy/dash/MainActivity;->imeOld:I

    invoke-virtual {v0, v3, v1, v3, v2}, Landroid/widget/FrameLayout;->setPadding(IIII)V

    return-void
.end method

.method askAuth()V
    .registers 3

    .prologue
    .line 858
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    if-eqz v0, :cond_5

    .line 876
    :goto_4
    return-void

    .line 859
    :cond_5
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->canAuth()Z

    move-result v0

    if-nez v0, :cond_f

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->authOk()V

    goto :goto_4

    .line 860
    :cond_f
    const/4 v0, 0x1

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    .line 861
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1c

    if-lt v0, v1, :cond_33

    .line 863
    :try_start_18
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    if-eqz v0, :cond_3a

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v0

    if-eqz v0, :cond_37

    const-string v0, "\u062a\u0623\u0643\u064a\u062f \u062a\u0634\u063a\u064a\u0644 \u0627\u0644\u0642\u0641\u0644 \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    :goto_26
    new-instance v1, Lcom/holy/dash/MainActivity$17;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$17;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-static {p0, v0, v1}, Lcom/holy/dash/Bio;->ask(Landroid/app/Activity;Ljava/lang/String;Lcom/holy/dash/Bio$Done;)V
    :try_end_2e
    .catch Ljava/lang/Throwable; {:try_start_18 .. :try_end_2e} :catch_2f

    goto :goto_4

    .line 871
    :catch_2f
    move-exception v0

    .line 872
    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    .line 875
    :cond_33
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->keyguard()V

    goto :goto_4

    .line 863
    :cond_37
    :try_start_37
    const-string v0, "\u062a\u0623\u0643\u064a\u062f \u0625\u064a\u0642\u0627\u0641 \u0627\u0644\u0642\u0641\u0644 \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    goto :goto_26

    :cond_3a
    const-string v0, "\u0627\u0641\u062a\u062d \u0644\u0648\u062d\u062a\u0643"
    :try_end_3c
    .catch Ljava/lang/Throwable; {:try_start_37 .. :try_end_3c} :catch_2f

    goto :goto_26
.end method

.method askBattery(Z)V
    .registers 6

    .prologue
    .line 733
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->batteryFree()Z

    move-result v0

    if-eqz v0, :cond_7

    .line 748
    :goto_6
    return-void

    .line 734
    :cond_7
    if-eqz p1, :cond_33

    .line 735
    new-instance v0, Landroid/app/AlertDialog$Builder;

    const v1, 0x10302d1

    invoke-direct {v0, p0, v1}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    const-string v1, "\ud83d\udd0b \u0644\u062a\u0635\u0644\u0643 \u0627\u0644\u0625\u0634\u0639\u0627\u0631\u0627\u062a \u0641\u064a \u0648\u0642\u062a\u0647\u0627"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0627\u0633\u0645\u062d \u0644\u0640 Holy \u0628\u0627\u0644\u0639\u0645\u0644 \u0641\u064a \u0627\u0644\u062e\u0644\u0641\u064a\u0629 \u062f\u0648\u0646 \u062a\u0642\u064a\u064a\u062f \u0627\u0644\u0628\u0637\u0627\u0631\u064a\u0629 \u2014 \u0644\u062a\u0635\u0644\u0643 \u0627\u0644\u0635\u0641\u0642\u0627\u062a \u0648\u0627\u0644\u062a\u0646\u0628\u064a\u0647\u0627\u062a \u0641\u0648\u0631\u0627\u064b \u062d\u062a\u0649 \u0648\u0627\u0644\u0634\u0627\u0634\u0629 \u0645\u0637\u0641\u0623\u0629.\n\u0627\u0633\u062a\u0647\u0644\u0627\u0643\u0647 \u0642\u0644\u064a\u0644: \u0637\u0644\u0628 \u0648\u0627\u062d\u062f \u064a\u0646\u062a\u0638\u0631 \u0627\u0644\u0644\u0648\u062d\u0629."

    .line 736
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0627\u0633\u0645\u062d"

    new-instance v2, Lcom/holy/dash/MainActivity$15;

    invoke-direct {v2, p0}, Lcom/holy/dash/MainActivity$15;-><init>(Lcom/holy/dash/MainActivity;)V

    .line 737
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0644\u0627\u062d\u0642\u0627\u064b"

    const/4 v2, 0x0

    .line 740
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    goto :goto_6

    .line 744
    :cond_33
    :try_start_33
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS"

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "package:"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageName()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v2

    invoke-direct {v0, v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_58
    .catch Ljava/lang/Exception; {:try_start_33 .. :try_end_58} :catch_59

    goto :goto_6

    .line 745
    :catch_59
    move-exception v0

    .line 746
    :try_start_5a
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.IGNORE_BATTERY_OPTIMIZATION_SETTINGS"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_64
    .catch Ljava/lang/Exception; {:try_start_5a .. :try_end_64} :catch_65

    goto :goto_6

    :catch_65
    move-exception v0

    goto :goto_6
.end method

.method askNotif()V
    .registers 4

    .prologue
    .line 702
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x21

    if-lt v0, v1, :cond_1c

    const-string v0, "android.permission.POST_NOTIFICATIONS"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-eqz v0, :cond_1c

    .line 703
    const/4 v0, 0x1

    new-array v0, v0, [Ljava/lang/String;

    const/4 v1, 0x0

    const-string v2, "android.permission.POST_NOTIFICATIONS"

    aput-object v2, v0, v1

    const/16 v1, 0xb

    invoke-virtual {p0, v0, v1}, Lcom/holy/dash/MainActivity;->requestPermissions([Ljava/lang/String;I)V

    .line 713
    :cond_1b
    :goto_1b
    return-void

    .line 706
    :cond_1c
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/NotificationManager;->areNotificationsEnabled()Z

    move-result v0

    if-nez v0, :cond_1b

    .line 708
    :try_start_26
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.settings.APP_NOTIFICATION_SETTINGS"

    invoke-direct {v0, v1}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v1, "android.provider.extra.APP_PACKAGE"

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageName()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v0, v1, v2}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v0

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_3a
    .catch Ljava/lang/Exception; {:try_start_26 .. :try_end_3a} :catch_3b

    goto :goto_1b

    .line 709
    :catch_3b
    move-exception v0

    goto :goto_1b
.end method

.method askOem()V
    .registers 4

    .prologue
    .line 686
    invoke-static {p0}, Lcom/holy/dash/Prefs;->setAskedOem(Landroid/content/Context;)V

    .line 687
    new-instance v0, Landroid/app/AlertDialog$Builder;

    const v1, 0x10302d1

    invoke-direct {v0, p0, v1}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    const-string v1, "\ud83d\ude80 \u0644\u062a\u0635\u0644\u0643 \u0627\u0644\u0625\u0634\u0639\u0627\u0631\u0627\u062a \u0648\u0627\u0644\u062a\u0637\u0628\u064a\u0642 \u0645\u063a\u0644\u0642"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "\u0647\u0627\u062a\u0641\u0643 ("

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    sget-object v2, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ") \u064a\u063a\u0644\u0642 \u0627\u0644\u062a\u0637\u0628\u064a\u0642\u0627\u062a \u0641\u064a \u0627\u0644\u062e\u0644\u0641\u064a\u0629 \u062a\u0644\u0642\u0627\u0626\u064a\u0627\u064b.\n\u0641\u064a \u0627\u0644\u0635\u0641\u062d\u0629 \u0627\u0644\u062a\u0627\u0644\u064a\u0629 \u0641\u0639\u0651\u0644 \u0644\u0640 Holy: \u00ab\u0627\u0644\u062a\u0634\u063a\u064a\u0644 \u0627\u0644\u062a\u0644\u0642\u0627\u0626\u064a\u00bb (Autostart) \u0623\u0648 \u00ab\u0628\u0644\u0627 \u0642\u064a\u0648\u062f\u00bb \u0644\u0644\u0628\u0637\u0627\u0631\u064a\u0629.\n\u0648\u0625\u0646 \u0623\u0645\u0643\u0646: \u0627\u0642\u0641\u0644 Holy \u0641\u064a \u0642\u0627\u0626\u0645\u0629 \u0627\u0644\u062a\u0637\u0628\u064a\u0642\u0627\u062a \u0627\u0644\u0623\u062e\u064a\u0631\u0629 \ud83d\udd12 \u0643\u064a \u0644\u0627 \u064a\u064f\u063a\u0644\u0642 \u062d\u064a\u0646 \u062a\u0645\u0633\u062d\u0647\u0627."

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 688
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0627\u0641\u062a\u062d \u0627\u0644\u0625\u0639\u062f\u0627\u062f"

    new-instance v2, Lcom/holy/dash/MainActivity$14;

    invoke-direct {v2, p0}, Lcom/holy/dash/MainActivity$14;-><init>(Lcom/holy/dash/MainActivity;)V

    .line 690
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0644\u0627\u062d\u0642\u0627\u064b"

    const/4 v2, 0x0

    .line 693
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 694
    return-void
.end method

.method authFail(Ljava/lang/String;)V
    .registers 3

    .prologue
    .line 908
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    if-eqz v0, :cond_b

    .line 909
    const/4 v0, 0x0

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    .line 910
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->refreshPanel()V

    .line 915
    :cond_a
    :goto_a
    return-void

    .line 913
    :cond_b
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-eqz v0, :cond_17

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->getVisibility()I

    move-result v0

    if-eqz v0, :cond_1a

    :cond_17
    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->pendingWeb:Z

    .line 914
    :cond_1a
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    if-eqz v0, :cond_a

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    if-nez p1, :cond_24

    const-string p1, "\u0627\u0636\u063a\u0637 \u0627\u0644\u0632\u0631 \u0644\u062a\u0641\u062a\u062d \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    :cond_24
    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    goto :goto_a
.end method

.method authOk()V
    .registers 4

    .prologue
    const/4 v2, 0x0

    .line 893
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v0

    sput-wide v0, Lcom/holy/dash/MainActivity;->unlockedAt:J

    .line 894
    const-wide/16 v0, 0x0

    iput-wide v0, p0, Lcom/holy/dash/MainActivity;->stoppedAt:J

    .line 895
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    if-eqz v0, :cond_29

    .line 896
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v0

    .line 897
    const/4 v1, 0x0

    iput-object v1, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    .line 898
    invoke-static {p0, v0}, Lcom/holy/dash/Prefs;->setLock(Landroid/content/Context;Z)V

    .line 899
    if-eqz v0, :cond_33

    const-string v0, "\ud83d\udd10 \u0627\u0644\u0642\u0641\u0644 \u0628\u0627\u0644\u0628\u0635\u0645\u0629 \u0645\u0641\u0639\u0651\u0644"

    :goto_1f
    invoke-static {p0, v0, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    .line 900
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->refreshPanel()V

    .line 902
    :cond_29
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->pendingWeb:Z

    if-eqz v0, :cond_36

    iput-boolean v2, p0, Lcom/holy/dash/MainActivity;->pendingWeb:Z

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->bioOpen()V

    .line 905
    :cond_32
    :goto_32
    return-void

    .line 899
    :cond_33
    const-string v0, "\ud83d\udd13 \u0623\u064f\u0648\u0642\u0641 \u0627\u0644\u0642\u0641\u0644 \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    goto :goto_1f

    .line 903
    :cond_36
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->hideLock()V

    .line 904
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->pageReady:Z

    if-eqz v0, :cond_32

    invoke-static {p0, v2}, Lcom/holy/dash/Updater;->check(Landroid/app/Activity;Z)V

    goto :goto_32
.end method

.method batteryFree()Z
    .registers 3

    .prologue
    .line 697
    const-string v0, "power"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/os/PowerManager;

    .line 698
    if-eqz v0, :cond_16

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/os/PowerManager;->isIgnoringBatteryOptimizations(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_16

    const/4 v0, 0x1

    :goto_15
    return v0

    :cond_16
    const/4 v0, 0x0

    goto :goto_15
.end method

.method bioDone(Ljava/lang/String;ILjava/lang/String;I)V
    .registers 11

    .prologue
    const/16 v5, 0x191

    const/4 v1, 0x0

    const/4 v0, 0x1

    .line 951
    if-eqz p3, :cond_74

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {p1, v2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_74

    .line 952
    invoke-virtual {p3}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_4b

    const-string v0, "[A-Za-z0-9_\\-]{16,200}"

    invoke-virtual {p3, v0}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v0

    if-eqz v0, :cond_4b

    .line 953
    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;

    move-result-object v0

    .line 954
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "holy_tok="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "; Path=/; Max-Age="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    mul-int/lit8 v2, p4, 0x3c

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "; HttpOnly; SameSite=Strict"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, p1, v1}, Landroid/webkit/CookieManager;->setCookie(Ljava/lang/String;Ljava/lang/String;)V

    .line 955
    invoke-virtual {v0}, Landroid/webkit/CookieManager;->flush()V

    .line 957
    :cond_4b
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    new-instance v1, Lcom/holy/dash/MainActivity$19;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$19;-><init>(Lcom/holy/dash/MainActivity;)V

    const-wide/16 v2, 0x1f40

    invoke-virtual {v0, v1, v2, v3}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 958
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_73

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V

    .line 972
    :cond_73
    :goto_73
    return-void

    .line 961
    :cond_74
    iput-boolean v1, p0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    .line 962
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->hideLock()V

    .line 963
    if-ne p2, v5, :cond_af

    .line 964
    const-string v2, ""

    invoke-static {p0, v2}, Lcom/holy/dash/Prefs;->setBio(Landroid/content/Context;Ljava/lang/String;)V

    .line 965
    const-string v2, "\ud83d\udd10 \u0644\u0645 \u062a\u0639\u062f \u0627\u0644\u0628\u0635\u0645\u0629 \u062a\u0641\u062a\u062d \u0627\u0644\u0644\u0648\u062d\u0629 \u2014 \u0627\u0643\u062a\u0628 \u0643\u0644\u0645\u0629 \u0627\u0644\u0633\u0631 \u0645\u0631\u0629 \u0648\u0627\u062d\u062f\u0629 \u062b\u0645 \u062a\u0639\u0648\u062f \u0627\u0644\u0628\u0635\u0645\u0629 \u0643\u0627\u0641\u064a\u0629"

    invoke-static {p0, v2, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v2

    invoke-virtual {v2}, Landroid/widget/Toast;->show()V

    .line 971
    :goto_89
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v2, :cond_73

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "(function(){var b=document.getElementById(\'bio\');if(b&&!"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    if-ne p2, v5, :cond_c7

    :goto_9c
    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ")b.style.display=\'\';else if(b)b.style.display=\'none\'})()"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    const/4 v1, 0x0

    invoke-virtual {v2, v0, v1}, Landroid/webkit/WebView;->evaluateJavascript(Ljava/lang/String;Landroid/webkit/ValueCallback;)V

    goto :goto_73

    .line 966
    :cond_af
    const/16 v2, 0x1ad

    if-ne p2, v2, :cond_bd

    .line 967
    const-string v2, "\ud83d\udeab \u0645\u062d\u0627\u0648\u0644\u0627\u062a \u0643\u062b\u064a\u0631\u0629 \u2014 \u0627\u0643\u062a\u0628 \u0643\u0644\u0645\u0629 \u0627\u0644\u0633\u0631 \u0623\u0648 \u0627\u0646\u062a\u0638\u0631 10 \u062f\u0642\u0627\u0626\u0642"

    invoke-static {p0, v2, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v2

    invoke-virtual {v2}, Landroid/widget/Toast;->show()V

    goto :goto_89

    .line 969
    :cond_bd
    const-string v2, "\ud83d\udce1 \u062a\u0639\u0630\u0651\u0631 \u0627\u0644\u0648\u0635\u0648\u0644 \u0625\u0644\u0649 \u0627\u0644\u0644\u0648\u062d\u0629 \u2014 \u0623\u0639\u062f \u0627\u0644\u0645\u062d\u0627\u0648\u0644\u0629 \u0623\u0648 \u0627\u0643\u062a\u0628 \u0643\u0644\u0645\u0629 \u0627\u0644\u0633\u0631"

    invoke-static {p0, v2, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v2

    invoke-virtual {v2}, Landroid/widget/Toast;->show()V

    goto :goto_89

    :cond_c7
    move v0, v1

    .line 971
    goto :goto_9c
.end method

.method bioOpen()V
    .registers 6

    .prologue
    .line 921
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v1

    invoke-static {p0}, Lcom/holy/dash/Prefs;->bio(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    .line 922
    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_20

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_20

    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v3

    if-nez v3, :cond_20

    iget-boolean v3, p0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    if-eqz v3, :cond_24

    :cond_20
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->hideLock()V

    .line 948
    :goto_23
    return-void

    .line 923
    :cond_24
    const/4 v3, 0x1

    iput-boolean v3, p0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    .line 924
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-eqz v3, :cond_3e

    iget-object v3, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v3}, Landroid/view/View;->getVisibility()I

    move-result v3

    if-nez v3, :cond_3e

    iget-object v3, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    if-eqz v3, :cond_3e

    iget-object v3, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    const-string v4, "\ud83d\udd13 \u064a\u0641\u062a\u062d \u0627\u0644\u0644\u0648\u062d\u0629\u2026"

    invoke-virtual {v3, v4}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 925
    :cond_3e
    new-instance v3, Ljava/lang/Thread;

    new-instance v4, Lcom/holy/dash/MainActivity$18;

    invoke-direct {v4, p0, v1, v2, v0}, Lcom/holy/dash/MainActivity$18;-><init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V

    const-string v0, "holy-bio"

    invoke-direct {v3, v4, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 947
    invoke-virtual {v3}, Ljava/lang/Thread;->start()V

    goto :goto_23
.end method

.method buildWeb()V
    .registers 8

    .prologue
    const/16 v6, 0x64

    const/4 v5, -0x1

    const/4 v4, 0x1

    const/4 v3, 0x0

    .line 416
    new-instance v0, Landroid/webkit/WebView;

    invoke-direct {v0, p0}, Landroid/webkit/WebView;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    .line 417
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    iget v1, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->setBackgroundColor(I)V

    .line 418
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->getSettings()Landroid/webkit/WebSettings;

    move-result-object v0

    .line 419
    invoke-virtual {v0, v4}, Landroid/webkit/WebSettings;->setJavaScriptEnabled(Z)V

    .line 420
    invoke-virtual {v0, v4}, Landroid/webkit/WebSettings;->setDomStorageEnabled(Z)V

    .line 421
    invoke-virtual {v0, v3}, Landroid/webkit/WebSettings;->setMediaPlaybackRequiresUserGesture(Z)V

    .line 422
    invoke-virtual {v0, v6}, Landroid/webkit/WebSettings;->setTextZoom(I)V

    .line 423
    invoke-virtual {v0, v4}, Landroid/webkit/WebSettings;->setUseWideViewPort(Z)V

    .line 424
    invoke-virtual {v0, v3}, Landroid/webkit/WebSettings;->setLoadWithOverviewMode(Z)V

    .line 425
    invoke-virtual {v0, v3}, Landroid/webkit/WebSettings;->setBuiltInZoomControls(Z)V

    .line 426
    invoke-virtual {v0, v3}, Landroid/webkit/WebSettings;->setSupportZoom(Z)V

    .line 427
    invoke-virtual {v0, v3}, Landroid/webkit/WebSettings;->setAllowFileAccess(Z)V

    .line 428
    invoke-virtual {v0, v3}, Landroid/webkit/WebSettings;->setAllowContentAccess(Z)V

    .line 429
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0}, Landroid/webkit/WebSettings;->getUserAgentString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " HolyApp/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "2.2"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/webkit/WebSettings;->setUserAgentString(Ljava/lang/String;)V

    .line 430
    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;

    move-result-object v0

    invoke-virtual {v0, v4}, Landroid/webkit/CookieManager;->setAcceptCookie(Z)V

    .line 431
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v1, Lcom/holy/dash/MainActivity$Bridge;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$Bridge;-><init>(Lcom/holy/dash/MainActivity;)V

    const-string v2, "HolyApp"

    invoke-virtual {v0, v1, v2}, Landroid/webkit/WebView;->addJavascriptInterface(Ljava/lang/Object;Ljava/lang/String;)V

    .line 432
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v1, Lcom/holy/dash/MainActivity$Client;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$Client;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->setWebViewClient(Landroid/webkit/WebViewClient;)V

    .line 433
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v1, Lcom/holy/dash/MainActivity$Chrome;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$Chrome;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->setWebChromeClient(Landroid/webkit/WebChromeClient;)V

    .line 434
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v2, v5, v5}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v3, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;ILandroid/view/ViewGroup$LayoutParams;)V

    .line 435
    new-instance v0, Landroid/widget/ProgressBar;

    const/4 v1, 0x0

    const v2, 0x1010078

    invoke-direct {v0, p0, v1, v2}, Landroid/widget/ProgressBar;-><init>(Landroid/content/Context;Landroid/util/AttributeSet;I)V

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    .line 436
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    invoke-virtual {v0, v6}, Landroid/widget/ProgressBar;->setMax(I)V

    .line 437
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    const v1, -0xdd2c12

    invoke-static {v1}, Landroid/content/res/ColorStateList;->valueOf(I)Landroid/content/res/ColorStateList;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/ProgressBar;->setProgressTintList(Landroid/content/res/ColorStateList;)V

    .line 438
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    invoke-static {v3}, Landroid/content/res/ColorStateList;->valueOf(I)Landroid/content/res/ColorStateList;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/ProgressBar;->setProgressBackgroundTintList(Landroid/content/res/ColorStateList;)V

    .line 439
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    const/high16 v3, 0x40400000    # 3.0f

    invoke-virtual {p0, v3}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v3

    const/16 v4, 0x30

    invoke-direct {v2, v5, v3, v4}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 440
    return-void
.end method

.method canAuth()Z
    .registers 2

    .prologue
    .line 784
    const-string v0, "keyguard"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/KeyguardManager;

    .line 785
    if-eqz v0, :cond_12

    invoke-virtual {v0}, Landroid/app/KeyguardManager;->isDeviceSecure()Z

    move-result v0

    if-eqz v0, :cond_12

    const/4 v0, 0x1

    :goto_11
    return v0

    :cond_12
    const/4 v0, 0x0

    goto :goto_11
.end method

.method connect(Z)V
    .registers 5

    .prologue
    .line 351
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v0}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v0

    invoke-interface {v0}, Landroid/text/Editable;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lcom/holy/dash/Net;->normalize(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 352
    if-nez v0, :cond_18

    .line 353
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const-string v1, "\u0627\u0644\u0639\u0646\u0648\u0627\u0646 \u063a\u064a\u0631 \u0635\u062d\u064a\u062d \u2014 \u0645\u062b\u0627\u0644: http://1.2.3.4:8099"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 379
    :goto_17
    return-void

    .line 356
    :cond_18
    if-eqz p1, :cond_1e

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->useOrigin(Ljava/lang/String;)V

    goto :goto_17

    .line 357
    :cond_1e
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const v2, -0x646c37

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setTextColor(I)V

    .line 358
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const-string v2, "\u23f3 \u062c\u0627\u0631\u064d \u0627\u0644\u062a\u062d\u0642\u0642 \u0645\u0646 \u0627\u0644\u0644\u0648\u062d\u0629\u2026"

    invoke-virtual {v1, v2}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 359
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/holy/dash/MainActivity$7;

    invoke-direct {v2, p0, v0}, Lcom/holy/dash/MainActivity$7;-><init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;)V

    const-string v0, "holy-check"

    invoke-direct {v1, v2, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 378
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    goto :goto_17
.end method

.method dp(F)I
    .registers 4

    .prologue
    .line 243
    const/4 v0, 0x1

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v1

    invoke-virtual {v1}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v1

    invoke-static {v0, p1, v1}, Landroid/util/TypedValue;->applyDimension(IFLandroid/util/DisplayMetrics;)F

    move-result v0

    float-to-int v0, v0

    return v0
.end method

.method handleIntent(Landroid/content/Intent;)V
    .registers 4

    .prologue
    .line 629
    if-nez p1, :cond_3

    .line 635
    :cond_2
    :goto_2
    return-void

    .line 630
    :cond_3
    const-string v0, "go"

    invoke-virtual {p1, v0}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    .line 631
    const-string v1, "go"

    invoke-virtual {p1, v1}, Landroid/content/Intent;->removeExtra(Ljava/lang/String;)V

    .line 632
    if-eqz v0, :cond_2

    .line 633
    const-string v1, "[a-z]{2,10}(:[^\\u0000-\\u001f]{0,120})?"

    invoke-virtual {v0, v1}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v1

    if-eqz v1, :cond_26

    :goto_18
    iput-object v0, p0, Lcom/holy/dash/MainActivity;->pendingGo:Ljava/lang/String;

    .line 634
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->pageReady:Z

    if-eqz v0, :cond_2

    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->errShown:Z

    if-nez v0, :cond_2

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->runGo()V

    goto :goto_2

    .line 633
    :cond_26
    const-string v0, ""

    goto :goto_18
.end method

.method hasBio()Z
    .registers 3

    .prologue
    .line 790
    :try_start_0
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1c

    if-lt v0, v1, :cond_b

    invoke-static {p0}, Lcom/holy/dash/Bio;->has(Landroid/content/Context;)Z

    move-result v0

    .line 792
    :goto_a
    return v0

    .line 790
    :cond_b
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v0

    const-string v1, "android.hardware.fingerprint"

    invoke-virtual {v0, v1}, Landroid/content/pm/PackageManager;->hasSystemFeature(Ljava/lang/String;)Z
    :try_end_14
    .catch Ljava/lang/Throwable; {:try_start_0 .. :try_end_14} :catch_16

    move-result v0

    goto :goto_a

    .line 791
    :catch_16
    move-exception v0

    .line 792
    const/4 v0, 0x0

    goto :goto_a
.end method

.method hideError()V
    .registers 3

    .prologue
    .line 621
    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->errShown:Z

    .line 622
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->retry:Ljava/lang/Runnable;

    invoke-virtual {v0, v1}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V

    .line 623
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    if-eqz v0, :cond_15

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/view/View;->setVisibility(I)V

    .line 624
    :cond_15
    return-void
.end method

.method hideKeyboard()V
    .registers 4

    .prologue
    .line 401
    :try_start_0
    const-string v0, "input_method"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/view/inputmethod/InputMethodManager;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    .line 402
    invoke-virtual {v1}, Landroid/widget/FrameLayout;->getWindowToken()Landroid/os/IBinder;

    move-result-object v1

    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2}, Landroid/view/inputmethod/InputMethodManager;->hideSoftInputFromWindow(Landroid/os/IBinder;I)Z
    :try_end_12
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_12} :catch_13

    .line 406
    :goto_12
    return-void

    .line 403
    :catch_13
    move-exception v0

    goto :goto_12
.end method

.method hideLock()V
    .registers 3

    .prologue
    .line 853
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-eqz v0, :cond_b

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/view/View;->setVisibility(I)V

    .line 854
    :cond_b
    return-void
.end method

.method immersive()V
    .registers 4

    .prologue
    .line 188
    invoke-static {p0}, Lcom/holy/dash/Prefs;->navBar(Landroid/content/Context;)Z

    move-result v1

    if-eqz v1, :cond_hideall

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->navShown()V

    return-void

    :cond_hideall
    .line 189
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    .line 190
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1e

    if-lt v1, v2, :cond_25

    .line 191
    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/view/Window;->setDecorFitsSystemWindows(Z)V

    .line 192
    invoke-virtual {v0}, Landroid/view/Window;->getInsetsController()Landroid/view/WindowInsetsController;

    move-result-object v0

    .line 193
    if-eqz v0, :cond_24

    .line 194
    invoke-static {}, Landroid/view/WindowInsets$Type;->statusBars()I

    move-result v1

    invoke-static {}, Landroid/view/WindowInsets$Type;->navigationBars()I

    move-result v2

    or-int/2addr v1, v2

    invoke-interface {v0, v1}, Landroid/view/WindowInsetsController;->hide(I)V

    .line 195
    const/4 v1, 0x2

    invoke-interface {v0, v1}, Landroid/view/WindowInsetsController;->setSystemBarsBehavior(I)V

    .line 202
    :cond_24
    :goto_24
    return-void

    .line 198
    :cond_25
    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const/16 v1, 0x1706

    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V

    goto :goto_24
.end method

.method navShown()V
    .registers 4

    .prologue
    .line 203
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1e

    if-lt v1, v2, :cond_old

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/view/Window;->setDecorFitsSystemWindows(Z)V

    invoke-virtual {v0}, Landroid/view/Window;->getInsetsController()Landroid/view/WindowInsetsController;

    move-result-object v0

    if-eqz v0, :cond_done

    invoke-static {}, Landroid/view/WindowInsets$Type;->statusBars()I

    move-result v1

    invoke-interface {v0, v1}, Landroid/view/WindowInsetsController;->hide(I)V

    invoke-static {}, Landroid/view/WindowInsets$Type;->navigationBars()I

    move-result v1

    invoke-interface {v0, v1}, Landroid/view/WindowInsetsController;->show(I)V

    const/4 v1, 0x2

    invoke-interface {v0, v1}, Landroid/view/WindowInsetsController;->setSystemBarsBehavior(I)V

    :cond_done
    return-void

    :cond_old
    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const/16 v1, 0x1104

    invoke-virtual {v0, v1}, Landroid/view/View;->setSystemUiVisibility(I)V

    goto :cond_done
.end method

.method insets()V
    .registers 3

    .prologue
    .line 206
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1e

    if-lt v0, v1, :cond_11

    .line 207
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    new-instance v1, Lcom/holy/dash/MainActivity$2;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$2;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/FrameLayout;->setOnApplyWindowInsetsListener(Landroid/view/View$OnApplyWindowInsetsListener;)V

    .line 237
    :goto_10
    return-void

    .line 216
    :cond_11
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x1c

    if-lt v0, v1, :cond_21

    .line 217
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    new-instance v1, Lcom/holy/dash/MainActivity$3;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$3;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/widget/FrameLayout;->setOnApplyWindowInsetsListener(Landroid/view/View$OnApplyWindowInsetsListener;)V

    .line 226
    :cond_21
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v0}, Landroid/widget/FrameLayout;->getViewTreeObserver()Landroid/view/ViewTreeObserver;

    move-result-object v0

    new-instance v1, Lcom/holy/dash/MainActivity$4;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$4;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v0, v1}, Landroid/view/ViewTreeObserver;->addOnGlobalLayoutListener(Landroid/view/ViewTreeObserver$OnGlobalLayoutListener;)V

    goto :goto_10
.end method

.method keyguard()V
    .registers 4

    .prologue
    .line 880
    const-string v0, "keyguard"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/KeyguardManager;

    .line 881
    if-nez v0, :cond_11

    const/4 v0, 0x0

    .line 882
    :goto_b
    if-nez v0, :cond_21

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->authOk()V

    .line 890
    :goto_10
    return-void

    .line 881
    :cond_11
    const-string v2, "Holy"

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->pendingLock:Ljava/lang/Boolean;

    if-eqz v1, :cond_1e

    const-string v1, "\u062a\u0623\u0643\u064a\u062f \u0627\u0644\u0642\u0641\u0644 \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    :goto_19
    invoke-virtual {v0, v2, v1}, Landroid/app/KeyguardManager;->createConfirmDeviceCredentialIntent(Ljava/lang/CharSequence;Ljava/lang/CharSequence;)Landroid/content/Intent;

    move-result-object v0

    goto :goto_b

    :cond_1e
    const-string v1, "\u0627\u0641\u062a\u062d \u0644\u0648\u062d\u062a\u0643"

    goto :goto_19

    .line 883
    :cond_21
    const/4 v1, 0x1

    iput-boolean v1, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    .line 885
    const/16 v1, 0xe

    :try_start_26
    invoke-virtual {p0, v0, v1}, Lcom/holy/dash/MainActivity;->startActivityForResult(Landroid/content/Intent;I)V
    :try_end_29
    .catch Ljava/lang/Exception; {:try_start_26 .. :try_end_29} :catch_2a

    goto :goto_10

    .line 886
    :catch_2a
    move-exception v0

    .line 887
    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    .line 888
    const-string v0, "\u062a\u0639\u0630\u0651\u0631 \u0641\u062a\u062d \u0634\u0627\u0634\u0629 \u0627\u0644\u0642\u0641\u0644"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->authFail(Ljava/lang/String;)V

    goto :goto_10
.end method

.method leave()V
    .registers 7

    .prologue
    .line 669
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 670
    iget-wide v2, p0, Lcom/holy/dash/MainActivity;->lastBack:J

    sub-long v2, v0, v2

    const-wide/16 v4, 0x7d0

    cmp-long v2, v2, v4

    if-gez v2, :cond_13

    const/4 v0, 0x1

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->moveTaskToBack(Z)Z

    .line 675
    :goto_12
    return-void

    .line 672
    :cond_13
    iput-wide v0, p0, Lcom/holy/dash/MainActivity;->lastBack:J

    .line 673
    const-string v0, "\u0627\u0636\u063a\u0637 \u0631\u062c\u0648\u0639 \u0645\u0631\u0629 \u0623\u062e\u0631\u0649 \u0644\u0644\u062e\u0631\u0648\u062c"

    const/4 v1, 0x0

    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    goto :goto_12
.end method

.method lockCheck()Z
    .registers 9

    .prologue
    const-wide/16 v6, 0x0

    const/4 v0, 0x1

    const/4 v1, 0x0

    .line 798
    invoke-static {p0}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v2

    if-eqz v2, :cond_e

    iget-boolean v2, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    if-eqz v2, :cond_1e

    :cond_e
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-eqz v2, :cond_1c

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v2}, Landroid/view/View;->getVisibility()I

    move-result v2

    if-nez v2, :cond_1c

    :goto_1a
    move v1, v0

    .line 809
    :goto_1b
    return v1

    :cond_1c
    move v0, v1

    .line 798
    goto :goto_1a

    .line 799
    :cond_1e
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->canAuth()Z

    move-result v2

    if-nez v2, :cond_34

    .line 800
    invoke-static {p0, v1}, Lcom/holy/dash/Prefs;->setLock(Landroid/content/Context;Z)V

    .line 801
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->hideLock()V

    .line 802
    const-string v2, "\ud83d\udd10 \u0644\u0645 \u064a\u0639\u062f \u0641\u064a \u0627\u0644\u0647\u0627\u062a\u0641 \u0642\u0641\u0644 \u0634\u0627\u0634\u0629 \u2014 \u0623\u064f\u0648\u0642\u0641 \u0642\u0641\u0644 Holy \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    invoke-static {p0, v2, v0}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    goto :goto_1b

    .line 805
    :cond_34
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v2

    .line 806
    sget-wide v4, Lcom/holy/dash/MainActivity;->unlockedAt:J

    cmp-long v4, v4, v6

    if-lez v4, :cond_5a

    iget-wide v4, p0, Lcom/holy/dash/MainActivity;->stoppedAt:J

    cmp-long v4, v4, v6

    if-eqz v4, :cond_4d

    iget-wide v4, p0, Lcom/holy/dash/MainActivity;->stoppedAt:J

    sub-long/2addr v2, v4

    const-wide/16 v4, 0x7530

    cmp-long v2, v2, v4

    if-gez v2, :cond_5a

    :cond_4d
    move v2, v0

    .line 807
    :goto_4e
    if-eqz v2, :cond_5c

    sget-wide v2, Lcom/holy/dash/MainActivity;->unlockedAt:J

    cmp-long v2, v2, v6

    if-lez v2, :cond_5c

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->hideLock()V

    goto :goto_1b

    :cond_5a
    move v2, v1

    .line 806
    goto :goto_4e

    .line 808
    :cond_5c
    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->showLock(Z)V

    move v1, v0

    .line 809
    goto :goto_1b
.end method

.method notifAllowed()Z
    .registers 3

    .prologue
    .line 680
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v1, 0x21

    if-lt v0, v1, :cond_10

    const-string v0, "android.permission.POST_NOTIFICATIONS"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->checkSelfPermission(Ljava/lang/String;)I

    move-result v0

    if-eqz v0, :cond_10

    const/4 v0, 0x0

    .line 681
    :goto_f
    return v0

    :cond_10
    invoke-static {p0}, Lcom/holy/dash/Notif;->nm(Landroid/content/Context;)Landroid/app/NotificationManager;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/NotificationManager;->areNotificationsEnabled()Z

    move-result v0

    goto :goto_f
.end method

.method protected onActivityResult(IILandroid/content/Intent;)V
    .registers 6

    .prologue
    .line 769
    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;->onActivityResult(IILandroid/content/Intent;)V

    .line 770
    const/16 v0, 0xe

    if-ne p1, v0, :cond_17

    .line 771
    const/4 v0, 0x0

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    .line 772
    const/4 v0, -0x1

    if-ne p2, v0, :cond_11

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->authOk()V

    .line 779
    :cond_10
    :goto_10
    return-void

    .line 772
    :cond_11
    const-string v0, "\u0644\u0645 \u064a\u064f\u0641\u062a\u062d \u2014 \u0623\u0639\u062f \u0627\u0644\u0645\u062d\u0627\u0648\u0644\u0629"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->authFail(Ljava/lang/String;)V

    goto :goto_10

    .line 775
    :cond_17
    const/16 v0, 0xd

    if-ne p1, v0, :cond_10

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    if-eqz v0, :cond_10

    .line 776
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    invoke-static {p2, p3}, Landroid/webkit/WebChromeClient$FileChooserParams;->parseResult(ILandroid/content/Intent;)[Landroid/net/Uri;

    move-result-object v1

    invoke-interface {v0, v1}, Landroid/webkit/ValueCallback;->onReceiveValue(Ljava/lang/Object;)V

    .line 777
    const/4 v0, 0x0

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    goto :goto_10
.end method

.method public onBackPressed()V
    .registers 4

    .prologue
    .line 653
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-eqz v0, :cond_11

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->getVisibility()I

    move-result v0

    if-nez v0, :cond_11

    const/4 v0, 0x1

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->moveTaskToBack(Z)Z

    .line 666
    :goto_10
    return-void

    .line 654
    :cond_11
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    if-eqz v0, :cond_2d

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->getVisibility()I

    move-result v0

    if-nez v0, :cond_2d

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_2d

    .line 655
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/view/View;->setVisibility(I)V

    goto :goto_10

    .line 658
    :cond_2d
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_35

    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->errShown:Z

    if-eqz v0, :cond_39

    :cond_35
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->leave()V

    goto :goto_10

    .line 659
    :cond_39
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    const-string v1, "(window.holyBack&&holyBack())?\'1\':\'0\'"

    new-instance v2, Lcom/holy/dash/MainActivity$13;

    invoke-direct {v2, p0}, Lcom/holy/dash/MainActivity$13;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v0, v1, v2}, Landroid/webkit/WebView;->evaluateJavascript(Ljava/lang/String;Landroid/webkit/ValueCallback;)V

    goto :goto_10
.end method

.method protected onCreate(Landroid/os/Bundle;)V
    .registers 6

    .prologue
    const/4 v3, 0x1

    .line 114
    invoke-super {p0, p1}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V

    .line 115
    invoke-static {p0}, Lcom/holy/dash/Prefs;->bg(Landroid/content/Context;)I

    move-result v0

    iput v0, p0, Lcom/holy/dash/MainActivity;->bg:I

    .line 116
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getWindow()Landroid/view/Window;

    move-result-object v0

    .line 117
    new-instance v1, Landroid/graphics/drawable/ColorDrawable;

    iget v2, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-direct {v1, v2}, Landroid/graphics/drawable/ColorDrawable;-><init>(I)V

    invoke-virtual {v0, v1}, Landroid/view/Window;->setBackgroundDrawable(Landroid/graphics/drawable/Drawable;)V

    .line 118
    iget v1, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v0, v1}, Landroid/view/Window;->setStatusBarColor(I)V

    .line 119
    iget v1, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v0, v1}, Landroid/view/Window;->setNavigationBarColor(I)V

    .line 120
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1c

    if-lt v1, v2, :cond_31

    .line 121
    invoke-virtual {v0}, Landroid/view/Window;->getAttributes()Landroid/view/WindowManager$LayoutParams;

    move-result-object v1

    .line 122
    iput v3, v1, Landroid/view/WindowManager$LayoutParams;->layoutInDisplayCutoutMode:I

    .line 123
    invoke-virtual {v0, v1}, Landroid/view/Window;->setAttributes(Landroid/view/WindowManager$LayoutParams;)V

    .line 125
    :cond_31
    new-instance v0, Landroid/widget/FrameLayout;

    invoke-direct {v0, p0}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    .line 126
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    iget v1, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v0, v1}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    .line 127
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {v0, v3}, Landroid/widget/FrameLayout;->setLayoutDirection(I)V

    .line 128
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->setContentView(Landroid/view/View;)V

    .line 129
    invoke-static {p0}, Lcom/holy/dash/Prefs;->fps(Landroid/content/Context;)I

    move-result v0

    invoke-static {p0, v0}, Lcom/holy/dash/Hz;->apply(Landroid/app/Activity;I)I

    .line 130
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->insets()V

    .line 131
    invoke-static {p0}, Lcom/holy/dash/Notif;->channels(Landroid/content/Context;)V

    .line 132
    invoke-static {p0}, Lcom/holy/dash/Prefs;->origin(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v0

    iput-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    .line 133
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getIntent()Landroid/content/Intent;

    move-result-object v0

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->handleIntent(Landroid/content/Intent;)V

    .line 134
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-eqz v0, :cond_81

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getIntent()Landroid/content/Intent;

    move-result-object v0

    if-nez v0, :cond_76

    const/4 v0, 0x0

    :goto_72
    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->showSetup(Ljava/lang/String;)V

    .line 136
    :goto_75
    return-void

    .line 134
    :cond_76
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getIntent()Landroid/content/Intent;

    move-result-object v0

    const-string v1, "url"

    invoke-virtual {v0, v1}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    goto :goto_72

    .line 135
    :cond_81
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->openDashboard()V

    goto :goto_75
.end method

.method protected onNewIntent(Landroid/content/Intent;)V
    .registers 2

    .prologue
    .line 140
    invoke-super {p0, p1}, Landroid/app/Activity;->onNewIntent(Landroid/content/Intent;)V

    .line 141
    invoke-virtual {p0, p1}, Lcom/holy/dash/MainActivity;->setIntent(Landroid/content/Intent;)V

    .line 142
    invoke-virtual {p0, p1}, Lcom/holy/dash/MainActivity;->handleIntent(Landroid/content/Intent;)V

    .line 143
    return-void
.end method

.method protected onPause()V
    .registers 2

    .prologue
    .line 172
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_e

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->onPause()V

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->pauseTimers()V

    .line 173
    :cond_e
    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;

    move-result-object v0

    invoke-virtual {v0}, Landroid/webkit/CookieManager;->flush()V

    .line 174
    invoke-super {p0}, Landroid/app/Activity;->onPause()V

    .line 175
    return-void
.end method

.method public onRequestPermissionsResult(I[Ljava/lang/String;[I)V
    .registers 8

    .prologue
    const/4 v0, 0x0

    const/4 v1, 0x1

    .line 752
    invoke-super {p0, p1, p2, p3}, Landroid/app/Activity;->onRequestPermissionsResult(I[Ljava/lang/String;[I)V

    .line 753
    array-length v2, p3

    if-lez v2, :cond_d

    aget v2, p3, v0

    if-nez v2, :cond_d

    move v0, v1

    .line 754
    :cond_d
    const/16 v2, 0xb

    if-ne p1, v2, :cond_1f

    if-eqz v0, :cond_1f

    invoke-static {p0}, Lcom/holy/dash/Prefs;->askedBattery(Landroid/content/Context;)Z

    move-result v2

    if-nez v2, :cond_1f

    .line 755
    invoke-static {p0}, Lcom/holy/dash/Prefs;->setAskedBattery(Landroid/content/Context;)V

    .line 756
    invoke-virtual {p0, v1}, Lcom/holy/dash/MainActivity;->askBattery(Z)V

    .line 758
    :cond_1f
    const/16 v2, 0xc

    if-ne p1, v2, :cond_35

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->pendingSave:[B

    if-eqz v2, :cond_35

    .line 759
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->pendingSave:[B

    .line 760
    const/4 v3, 0x0

    iput-object v3, p0, Lcom/holy/dash/MainActivity;->pendingSave:[B

    .line 761
    if-eqz v0, :cond_39

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingSaveName:Ljava/lang/String;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->pendingSaveMime:Ljava/lang/String;

    invoke-virtual {p0, v0, v1, v2}, Lcom/holy/dash/MainActivity;->saveNow(Ljava/lang/String;Ljava/lang/String;[B)V

    .line 764
    :cond_35
    :goto_35
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->refreshPanel()V

    .line 765
    return-void

    .line 762
    :cond_39
    const-string v0, "\u0644\u0627 \u064a\u0645\u0643\u0646 \u0627\u0644\u062d\u0641\u0638 \u062f\u0648\u0646 \u0625\u0630\u0646 \u0627\u0644\u062a\u062e\u0632\u064a\u0646 \u2014 \u062c\u0631\u0651\u0628 \u00ab\u0645\u0634\u0627\u0631\u0643\u0629\u00bb"

    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    goto :goto_35
.end method

.method protected onResume()V
    .registers 3

    .prologue
    .line 147
    invoke-super {p0}, Landroid/app/Activity;->onResume()V

    .line 148
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->immersive()V

    .line 149
    invoke-static {p0}, Lcom/holy/dash/Prefs;->fps(Landroid/content/Context;)I

    move-result v0

    invoke-static {p0, v0}, Lcom/holy/dash/Hz;->apply(Landroid/app/Activity;I)I

    .line 150
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_1b

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->onResume()V

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    invoke-virtual {v0}, Landroid/webkit/WebView;->resumeTimers()V

    .line 151
    :cond_1b
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->lockCheck()Z

    move-result v0

    .line 152
    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v1

    if-eqz v1, :cond_48

    .line 153
    invoke-static {p0}, Lcom/holy/dash/WatchService;->start(Landroid/content/Context;)V

    .line 154
    invoke-static {p0}, Lcom/holy/dash/Keep;->schedule(Landroid/content/Context;)V

    .line 155
    if-nez v0, :cond_48

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v1

    if-eqz v1, :cond_48

    invoke-static {}, Lcom/holy/dash/Oem;->strict()Z

    move-result v1

    if-eqz v1, :cond_48

    invoke-static {p0}, Lcom/holy/dash/Prefs;->askedOem(Landroid/content/Context;)Z

    move-result v1

    if-nez v1, :cond_48

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->batteryFree()Z

    move-result v1

    if-eqz v1, :cond_48

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->askOem()V

    .line 157
    :cond_48
    iget-boolean v1, p0, Lcom/holy/dash/MainActivity;->pageReady:Z

    if-eqz v1, :cond_52

    if-nez v0, :cond_52

    const/4 v0, 0x0

    invoke-static {p0, v0}, Lcom/holy/dash/Updater;->check(Landroid/app/Activity;Z)V

    .line 158
    :cond_52
    return-void
.end method

.method protected onStop()V
    .registers 3

    .prologue
    .line 162
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->refreshAsync(Landroid/content/Context;)V

    .line 163
    invoke-static {p0}, Lcom/holy/dash/Prefs;->lock(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_17

    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->authBusy:Z

    if-nez v0, :cond_17

    .line 164
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v0

    iput-wide v0, p0, Lcom/holy/dash/MainActivity;->stoppedAt:J

    .line 165
    const/4 v0, 0x0

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->showLock(Z)V

    .line 167
    :cond_17
    invoke-super {p0}, Landroid/app/Activity;->onStop()V

    .line 168
    return-void
.end method

.method public onWindowFocusChanged(Z)V
    .registers 3

    .prologue
    .line 179
    invoke-super {p0, p1}, Landroid/app/Activity;->onWindowFocusChanged(Z)V

    .line 180
    if-eqz p1, :cond_1b

    .line 181
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->immersive()V

    .line 182
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    if-eqz v0, :cond_1b

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->getVisibility()I

    move-result v0

    if-nez v0, :cond_1b

    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->clipTried:Z

    if-nez v0, :cond_1b

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->pasteFromClipboard()V

    .line 184
    :cond_1b
    return-void
.end method

.method openDashboard()V
    .registers 4

    .prologue
    .line 411
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-nez v0, :cond_7

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->buildWeb()V

    .line 412
    :cond_7
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V

    .line 413
    return-void
.end method

.method openWatchSettings()V
    .registers 7

    .prologue
    const/4 v5, 0x1

    const/4 v1, 0x0

    .line 717
    sget v0, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1a

    if-lt v0, v2, :cond_42

    .line 718
    const/4 v0, 0x2

    new-array v0, v0, [Landroid/content/Intent;

    new-instance v2, Landroid/content/Intent;

    const-string v3, "android.settings.CHANNEL_NOTIFICATION_SETTINGS"

    invoke-direct {v2, v3}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v3, "android.provider.extra.APP_PACKAGE"

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageName()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v2

    const-string v3, "android.provider.extra.CHANNEL_ID"

    const-string v4, "watch"

    .line 719
    invoke-virtual {v2, v3, v4}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v2

    aput-object v2, v0, v1

    new-instance v2, Landroid/content/Intent;

    const-string v3, "android.settings.APP_NOTIFICATION_SETTINGS"

    invoke-direct {v2, v3}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    const-string v3, "android.provider.extra.APP_PACKAGE"

    .line 720
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageName()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v2

    aput-object v2, v0, v5

    .line 722
    :goto_39
    array-length v2, v0

    :goto_3a
    if-ge v1, v2, :cond_41

    aget-object v3, v0, v1

    .line 724
    :try_start_3e
    invoke-virtual {p0, v3}, Lcom/holy/dash/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_41
    .catch Ljava/lang/Exception; {:try_start_3e .. :try_end_41} :catch_69

    .line 730
    :cond_41
    return-void

    .line 721
    :cond_42
    new-array v0, v5, [Landroid/content/Intent;

    new-instance v2, Landroid/content/Intent;

    const-string v3, "android.settings.APPLICATION_DETAILS_SETTINGS"

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "package:"

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getPackageName()Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v4

    invoke-direct {v2, v3, v4}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V

    aput-object v2, v0, v1

    goto :goto_39

    .line 726
    :catch_69
    move-exception v3

    .line 722
    add-int/lit8 v1, v1, 0x1

    goto :goto_3a
.end method

.method ours(Landroid/net/Uri;)Z
    .registers 4

    .prologue
    .line 443
    if-eqz p1, :cond_1c

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_1c

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {p1}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v1}, Lcom/holy/dash/Net;->originOf(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1c

    const/4 v0, 0x1

    :goto_1b
    return v0

    :cond_1c
    const/4 v0, 0x0

    goto :goto_1b
.end method

.method pasteFromClipboard()V
    .registers 4

    .prologue
    .line 337
    const/4 v0, 0x1

    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->clipTried:Z

    .line 339
    :try_start_3
    const-string v0, "clipboard"

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/content/ClipboardManager;

    .line 340
    if-eqz v0, :cond_1f

    invoke-virtual {v0}, Landroid/content/ClipboardManager;->hasPrimaryClip()Z

    move-result v1

    if-eqz v1, :cond_1f

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v1}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v1

    invoke-interface {v1}, Landroid/text/Editable;->length()I

    move-result v1

    if-lez v1, :cond_20

    .line 348
    :cond_1f
    :goto_1f
    return-void

    .line 341
    :cond_20
    invoke-virtual {v0}, Landroid/content/ClipboardManager;->getPrimaryClip()Landroid/content/ClipData;

    move-result-object v0

    .line 342
    if-eqz v0, :cond_1f

    invoke-virtual {v0}, Landroid/content/ClipData;->getItemCount()I

    move-result v1

    if-eqz v1, :cond_1f

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/content/ClipData;->getItemAt(I)Landroid/content/ClipData$Item;

    move-result-object v1

    invoke-virtual {v1}, Landroid/content/ClipData$Item;->getText()Ljava/lang/CharSequence;

    move-result-object v1

    if-eqz v1, :cond_1f

    .line 343
    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/content/ClipData;->getItemAt(I)Landroid/content/ClipData$Item;

    move-result-object v0

    invoke-virtual {v0}, Landroid/content/ClipData$Item;->getText()Ljava/lang/CharSequence;

    move-result-object v0

    invoke-interface {v0}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/String;->trim()Ljava/lang/String;

    move-result-object v0

    .line 344
    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v1

    const/16 v2, 0xc8

    if-ge v1, v2, :cond_1f

    const-string v1, "(?i)^https?://[^\\s]+$"

    invoke-virtual {v0, v1}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v1

    if-eqz v1, :cond_1f

    invoke-static {v0}, Lcom/holy/dash/Net;->normalize(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    if-eqz v1, :cond_1f

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-static {v0}, Lcom/holy/dash/Net;->normalize(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Landroid/widget/EditText;->setText(Ljava/lang/CharSequence;)V
    :try_end_67
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_67} :catch_68

    goto :goto_1f

    .line 345
    :catch_68
    move-exception v0

    goto :goto_1f
.end method

.method refreshPanel()V
    .registers 4

    .prologue
    .line 975
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v0, :cond_10

    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->pageReady:Z

    if-eqz v0, :cond_10

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    const-string v1, "window.appRender&&document.querySelector(\'#ap_body\')&&appRender()"

    const/4 v2, 0x0

    invoke-virtual {v0, v1, v2}, Landroid/webkit/WebView;->evaluateJavascript(Ljava/lang/String;Landroid/webkit/ValueCallback;)V

    .line 976
    :cond_10
    return-void
.end method

.method runGo()V
    .registers 5

    .prologue
    .line 639
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->pendingGo:Ljava/lang/String;

    .line 640
    const/4 v1, 0x0

    iput-object v1, p0, Lcom/holy/dash/MainActivity;->pendingGo:Ljava/lang/String;

    .line 641
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-eqz v1, :cond_11

    if-eqz v0, :cond_11

    invoke-virtual {v0}, Ljava/lang/String;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_12

    .line 647
    :cond_11
    :goto_11
    return-void

    .line 642
    :cond_12
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "window.holyGo?(holyGo("

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-static {v0}, Lorg/json/JSONObject;->quote(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, "),\'1\'):\'0\'"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    new-instance v3, Lcom/holy/dash/MainActivity$12;

    invoke-direct {v3, p0, v0}, Lcom/holy/dash/MainActivity$12;-><init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;)V

    invoke-virtual {v1, v2, v3}, Landroid/webkit/WebView;->evaluateJavascript(Ljava/lang/String;Landroid/webkit/ValueCallback;)V

    goto :goto_11
.end method

.method saveNow(Ljava/lang/String;Ljava/lang/String;[B)V
    .registers 10

    .prologue
    const/4 v0, 0x0

    const/4 v5, 0x1

    .line 988
    .line 989
    :try_start_2
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1d

    if-lt v1, v2, :cond_a4

    .line 990
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v1

    .line 991
    new-instance v2, Landroid/content/ContentValues;

    invoke-direct {v2}, Landroid/content/ContentValues;-><init>()V

    .line 992
    const-string v0, "_display_name"

    invoke-virtual {v2, v0, p1}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 993
    const-string v0, "mime_type"

    invoke-virtual {v2, v0, p2}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 994
    const-string v0, "relative_path"

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    sget-object v4, Landroid/os/Environment;->DIRECTORY_DOWNLOADS:Ljava/lang/String;

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, "/Holy"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v0, v3}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/String;)V

    .line 995
    const-string v0, "is_pending"

    const/4 v3, 0x1

    invoke-static {v3}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v3

    invoke-virtual {v2, v0, v3}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Integer;)V

    .line 996
    sget-object v0, Landroid/provider/MediaStore$Downloads;->EXTERNAL_CONTENT_URI:Landroid/net/Uri;

    invoke-virtual {v1, v0, v2}, Landroid/content/ContentResolver;->insert(Landroid/net/Uri;Landroid/content/ContentValues;)Landroid/net/Uri;

    move-result-object v0

    .line 997
    if-nez v0, :cond_5a

    new-instance v0, Ljava/io/IOException;

    const-string v1, "insert"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_4f
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_4f} :catch_4f

    .line 1014
    :catch_4f
    move-exception v0

    .line 1015
    const-string v0, "\u062a\u0639\u0630\u0651\u0631 \u0627\u0644\u062d\u0641\u0638 \u2014 \u062c\u0631\u0651\u0628 \u00ab\u0645\u0634\u0627\u0631\u0643\u0629\u00bb"

    invoke-static {p0, v0, v5}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    .line 1017
    :goto_59
    return-void

    .line 998
    :cond_5a
    :try_start_5a
    invoke-virtual {v1, v0}, Landroid/content/ContentResolver;->openOutputStream(Landroid/net/Uri;)Ljava/io/OutputStream;

    move-result-object v3

    .line 999
    if-nez v3, :cond_68

    new-instance v0, Ljava/io/IOException;

    const-string v1, "open"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_68
    .catch Ljava/lang/Exception; {:try_start_5a .. :try_end_68} :catch_4f

    .line 1000
    :cond_68
    :try_start_68
    invoke-virtual {v3, p3}, Ljava/io/OutputStream;->write([B)V
    :try_end_6b
    .catchall {:try_start_68 .. :try_end_6b} :catchall_9f

    :try_start_6b
    invoke-virtual {v3}, Ljava/io/OutputStream;->close()V

    .line 1001
    invoke-virtual {v2}, Landroid/content/ContentValues;->clear()V

    .line 1002
    const-string v3, "is_pending"

    const/4 v4, 0x0

    invoke-static {v4}, Ljava/lang/Integer;->valueOf(I)Ljava/lang/Integer;

    move-result-object v4

    invoke-virtual {v2, v3, v4}, Landroid/content/ContentValues;->put(Ljava/lang/String;Ljava/lang/Integer;)V

    .line 1003
    const/4 v3, 0x0

    const/4 v4, 0x0

    invoke-virtual {v1, v0, v2, v3, v4}, Landroid/content/ContentResolver;->update(Landroid/net/Uri;Landroid/content/ContentValues;Ljava/lang/String;[Ljava/lang/String;)I

    .line 1012
    :goto_80
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v2, "\u2b07\ufe0f \u062d\u064f\u0641\u0638 \u0641\u064a \u0627\u0644\u062a\u0646\u0632\u064a\u0644\u0627\u062a/Holy: "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    const/4 v2, 0x1

    invoke-static {p0, v1, v2}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v1

    invoke-virtual {v1}, Landroid/widget/Toast;->show()V

    .line 1013
    invoke-static {p0, p1, v0, p2}, Lcom/holy/dash/Notif;->saved(Landroid/content/Context;Ljava/lang/String;Landroid/net/Uri;Ljava/lang/String;)V

    goto :goto_59

    .line 1000
    :catchall_9f
    move-exception v0

    invoke-virtual {v3}, Ljava/io/OutputStream;->close()V

    throw v0

    .line 1005
    :cond_a4
    new-instance v1, Ljava/io/File;

    sget-object v2, Landroid/os/Environment;->DIRECTORY_DOWNLOADS:Ljava/lang/String;

    invoke-static {v2}, Landroid/os/Environment;->getExternalStoragePublicDirectory(Ljava/lang/String;)Ljava/io/File;

    move-result-object v2

    const-string v3, "Holy"

    invoke-direct {v1, v2, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 1006
    invoke-virtual {v1}, Ljava/io/File;->isDirectory()Z

    move-result v2

    if-nez v2, :cond_c5

    invoke-virtual {v1}, Ljava/io/File;->mkdirs()Z

    move-result v2

    if-nez v2, :cond_c5

    new-instance v0, Ljava/io/IOException;

    const-string v1, "mkdir"

    invoke-direct {v0, v1}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 1007
    :cond_c5
    new-instance v2, Ljava/io/File;

    invoke-direct {v2, v1, p1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 1008
    new-instance v1, Ljava/io/FileOutputStream;

    invoke-direct {v1, v2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_cf
    .catch Ljava/lang/Exception; {:try_start_6b .. :try_end_cf} :catch_4f

    .line 1009
    :try_start_cf
    invoke-virtual {v1, p3}, Ljava/io/FileOutputStream;->write([B)V
    :try_end_d2
    .catchall {:try_start_cf .. :try_end_d2} :catchall_ea

    :try_start_d2
    invoke-virtual {v1}, Ljava/io/FileOutputStream;->close()V

    .line 1010
    const/4 v1, 0x1

    new-array v1, v1, [Ljava/lang/String;

    const/4 v3, 0x0

    invoke-virtual {v2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v2

    aput-object v2, v1, v3

    const/4 v2, 0x1

    new-array v2, v2, [Ljava/lang/String;

    const/4 v3, 0x0

    aput-object p2, v2, v3

    const/4 v3, 0x0

    invoke-static {p0, v1, v2, v3}, Landroid/media/MediaScannerConnection;->scanFile(Landroid/content/Context;[Ljava/lang/String;[Ljava/lang/String;Landroid/media/MediaScannerConnection$OnScanCompletedListener;)V

    goto :goto_80

    .line 1009
    :catchall_ea
    move-exception v0

    invoke-virtual {v1}, Ljava/io/FileOutputStream;->close()V

    throw v0
    :try_end_ef
    .catch Ljava/lang/Exception; {:try_start_d2 .. :try_end_ef} :catch_4f
.end method

.method setupLongPress(Ljava/lang/String;)V
    .registers 5

    .prologue
    .line 382
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v0}, Landroid/widget/EditText;->getParent()Landroid/view/ViewParent;

    move-result-object v0

    check-cast v0, Landroid/view/ViewGroup;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v1}, Landroid/widget/EditText;->getParent()Landroid/view/ViewParent;

    move-result-object v1

    check-cast v1, Landroid/view/ViewGroup;

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v1, v2}, Landroid/view/ViewGroup;->indexOfChild(Landroid/view/View;)I

    move-result v1

    add-int/lit8 v1, v1, 0x1

    invoke-virtual {v0, v1}, Landroid/view/ViewGroup;->getChildAt(I)Landroid/view/View;

    move-result-object v0

    .line 383
    new-instance v1, Lcom/holy/dash/MainActivity$8;

    invoke-direct {v1, p0, p1}, Lcom/holy/dash/MainActivity$8;-><init>(Lcom/holy/dash/MainActivity;Ljava/lang/String;)V

    invoke-virtual {v0, v1}, Landroid/view/View;->setOnLongClickListener(Landroid/view/View$OnLongClickListener;)V

    .line 386
    return-void
.end method

.method share(Ljava/lang/String;Ljava/lang/String;[BLjava/lang/String;)V
    .registers 8

    .prologue
    .line 1021
    :try_start_0
    new-instance v0, Ljava/io/File;

    invoke-static {p0}, Lcom/holy/dash/FileShare;->dir(Landroid/content/Context;)Ljava/io/File;

    move-result-object v1

    invoke-direct {v0, v1, p1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 1022
    new-instance v1, Ljava/io/FileOutputStream;

    invoke-direct {v1, v0}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V
    :try_end_e
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_e} :catch_51

    .line 1023
    :try_start_e
    invoke-virtual {v1, p3}, Ljava/io/FileOutputStream;->write([B)V
    :try_end_11
    .catchall {:try_start_e .. :try_end_11} :catchall_4c

    :try_start_11
    invoke-virtual {v1}, Ljava/io/FileOutputStream;->close()V

    .line 1024
    invoke-static {v0}, Lcom/holy/dash/FileShare;->uriFor(Ljava/io/File;)Landroid/net/Uri;

    move-result-object v0

    .line 1025
    new-instance v1, Landroid/content/Intent;

    const-string v2, "android.intent.action.SEND"

    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, p2}, Landroid/content/Intent;->setType(Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v1

    const-string v2, "android.intent.extra.STREAM"

    invoke-virtual {v1, v2, v0}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Landroid/os/Parcelable;)Landroid/content/Intent;

    move-result-object v1

    const/4 v2, 0x1

    .line 1026
    invoke-virtual {v1, v2}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    move-result-object v1

    .line 1027
    if-eqz p4, :cond_3b

    invoke-virtual {p4}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-nez v2, :cond_3b

    const-string v2, "android.intent.extra.TEXT"

    invoke-virtual {v1, v2, p4}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    .line 1028
    :cond_3b
    invoke-static {p1, v0}, Landroid/content/ClipData;->newRawUri(Ljava/lang/CharSequence;Landroid/net/Uri;)Landroid/content/ClipData;

    move-result-object v0

    invoke-virtual {v1, v0}, Landroid/content/Intent;->setClipData(Landroid/content/ClipData;)V

    .line 1029
    const-string v0, "\u0645\u0634\u0627\u0631\u0643\u0629"

    invoke-static {v1, v0}, Landroid/content/Intent;->createChooser(Landroid/content/Intent;Ljava/lang/CharSequence;)Landroid/content/Intent;

    move-result-object v0

    invoke-virtual {p0, v0}, Lcom/holy/dash/MainActivity;->startActivity(Landroid/content/Intent;)V

    .line 1033
    :goto_4b
    return-void

    .line 1023
    :catchall_4c
    move-exception v0

    invoke-virtual {v1}, Ljava/io/FileOutputStream;->close()V

    throw v0
    :try_end_51
    .catch Ljava/lang/Exception; {:try_start_11 .. :try_end_51} :catch_51

    .line 1030
    :catch_51
    move-exception v0

    .line 1031
    const-string v0, "\u062a\u0639\u0630\u0651\u0631\u062a \u0627\u0644\u0645\u0634\u0627\u0631\u0643\u0629"

    const/4 v1, 0x0

    invoke-static {p0, v0, v1}, Landroid/widget/Toast;->makeText(Landroid/content/Context;Ljava/lang/CharSequence;I)Landroid/widget/Toast;

    move-result-object v0

    invoke-virtual {v0}, Landroid/widget/Toast;->show()V

    goto :goto_4b
.end method

.method showError(Ljava/lang/String;)V
    .registers 10

    .prologue
    const/4 v7, -0x1

    const/4 v6, 0x1

    const/high16 v4, 0x41e00000    # 28.0f

    const/4 v5, 0x0

    .line 583
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    if-nez v0, :cond_a0

    .line 584
    new-instance v0, Landroid/widget/LinearLayout;

    invoke-direct {v0, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 585
    invoke-virtual {v0, v6}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 586
    const/16 v1, 0x11

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 587
    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v1

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v2

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v3

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {v0, v1, v2, v3, v4}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 588
    iget v1, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->setBackgroundColor(I)V

    .line 589
    invoke-virtual {v0, v6}, Landroid/widget/LinearLayout;->setClickable(Z)V

    .line 590
    const-string v1, "\ud83d\udce1 \u062a\u0639\u0630\u0651\u0631 \u0627\u0644\u0648\u0635\u0648\u0644 \u0625\u0644\u0649 \u0627\u0644\u0644\u0648\u062d\u0629"

    const/high16 v2, 0x41980000    # 19.0f

    const v3, -0x131801

    invoke-virtual {p0, v1, v2, v3, v6}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v1

    .line 591
    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 592
    const-string v1, ""

    const/high16 v2, 0x41480000    # 12.5f

    const v3, -0x646c37

    invoke-virtual {p0, v1, v2, v3, v5}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v1

    iput-object v1, p0, Lcom/holy/dash/MainActivity;->errText:Landroid/widget/TextView;

    .line 593
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->errText:Landroid/widget/TextView;

    const/high16 v2, 0x41000000    # 8.0f

    invoke-virtual {p0, v2}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v2

    const/high16 v3, 0x41900000    # 18.0f

    invoke-virtual {p0, v3}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v3

    invoke-virtual {v1, v5, v2, v5, v3}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 594
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->errText:Landroid/widget/TextView;

    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 595
    new-instance v1, Landroid/widget/Button;

    invoke-direct {v1, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 596
    const-string v2, "\ud83d\udd04 \u0623\u0639\u062f \u0627\u0644\u0645\u062d\u0627\u0648\u0644\u0629"

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 597
    invoke-virtual {v1, v5}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 598
    new-instance v2, Lcom/holy/dash/MainActivity$10;

    invoke-direct {v2, p0}, Lcom/holy/dash/MainActivity$10;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 601
    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 602
    new-instance v1, Landroid/widget/Button;

    invoke-direct {v1, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 603
    const-string v2, "\ud83d\udd17 \u062a\u063a\u064a\u064a\u0631 \u0627\u0644\u0639\u0646\u0648\u0627\u0646"

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 604
    invoke-virtual {v1, v5}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 605
    new-instance v2, Lcom/holy/dash/MainActivity$11;

    invoke-direct {v2, p0}, Lcom/holy/dash/MainActivity$11;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v1, v2}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 608
    invoke-virtual {v0, v1}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 609
    iput-object v0, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    .line 610
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v2, v7, v7}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 612
    :cond_a0
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->errText:Landroid/widget/TextView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    iget-object v2, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "\n\u0625\u0630\u0627 \u0643\u0627\u0646\u062a \u0627\u0644\u0644\u0648\u062d\u0629 \u062a\u062a\u062d\u062f\u062b \u0623\u0648 \u062a\u0639\u064a\u062f \u0627\u0644\u062a\u0634\u063a\u064a\u0644\u060c \u062a\u0639\u0648\u062f \u062a\u0644\u0642\u0627\u0626\u064a\u0627\u064b \u062e\u0644\u0627\u0644 \u062b\u0648\u0627\u0646\u064d.\n("

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, ")"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 613
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    invoke-virtual {v0, v5}, Landroid/view/View;->setVisibility(I)V

    .line 614
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->err:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->bringToFront()V

    .line 615
    iput-boolean v6, p0, Lcom/holy/dash/MainActivity;->errShown:Z

    .line 616
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->retry:Ljava/lang/Runnable;

    invoke-virtual {v0, v1}, Landroid/os/Handler;->removeCallbacks(Ljava/lang/Runnable;)V

    .line 617
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    iget-object v1, p0, Lcom/holy/dash/MainActivity;->retry:Ljava/lang/Runnable;

    const-wide/16 v2, 0x1388

    invoke-virtual {v0, v1, v2, v3}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 618
    return-void
.end method

.method showLock(Z)V
    .registers 12

    .prologue
    const/4 v9, -0x1

    const/4 v8, -0x2

    const/high16 v5, 0x42a80000    # 84.0f

    const/4 v7, 0x1

    const/4 v6, 0x0

    .line 813
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-nez v0, :cond_d7

    .line 814
    new-instance v0, Landroid/widget/FrameLayout;

    invoke-direct {v0, p0}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    .line 815
    iget v1, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v0, v1}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    .line 816
    invoke-virtual {v0, v7}, Landroid/widget/FrameLayout;->setClickable(Z)V

    .line 817
    new-instance v1, Landroid/widget/LinearLayout;

    invoke-direct {v1, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 818
    invoke-virtual {v1, v7}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 819
    invoke-virtual {v1, v7}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 820
    new-instance v2, Landroid/widget/ImageView;

    invoke-direct {v2, p0}, Landroid/widget/ImageView;-><init>(Landroid/content/Context;)V

    .line 821
    const/high16 v3, 0x7f020000

    invoke-virtual {v2, v3}, Landroid/widget/ImageView;->setImageResource(I)V

    .line 822
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-direct {v3, v4, v5}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 823
    const-string v2, "Holy \u0645\u0642\u0641\u0644 \ud83d\udd10"

    const/high16 v3, 0x41a00000    # 20.0f

    const v4, -0x131801

    invoke-virtual {p0, v2, v3, v4, v7}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v2

    .line 824
    const/high16 v3, 0x41800000    # 16.0f

    invoke-virtual {p0, v3}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v3

    const/high16 v4, 0x40c00000    # 6.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {v2, v6, v3, v6, v4}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 825
    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 826
    const-string v2, "\u0627\u0641\u062a\u062d \u0628\u0627\u0644\u0628\u0635\u0645\u0629 \u0644\u062a\u0631\u0649 \u0644\u0648\u062d\u062a\u0643"

    const/high16 v3, 0x41500000    # 13.0f

    const v4, -0x646c37

    invoke-virtual {p0, v2, v3, v4, v6}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v2

    iput-object v2, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    .line 827
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    invoke-virtual {v1, v2}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 828
    new-instance v2, Landroid/widget/Button;

    invoke-direct {v2, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 829
    const-string v3, "\ud83d\udd13 \u0627\u0641\u062a\u062d \u0628\u0627\u0644\u0628\u0635\u0645\u0629"

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 830
    invoke-virtual {v2, v6}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 831
    const v3, -0xf7eee4

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setTextColor(I)V

    .line 832
    sget-object v3, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;)V

    .line 833
    new-instance v3, Landroid/graphics/drawable/GradientDrawable;

    sget-object v4, Landroid/graphics/drawable/GradientDrawable$Orientation;->LEFT_RIGHT:Landroid/graphics/drawable/GradientDrawable$Orientation;

    const/4 v5, 0x2

    new-array v5, v5, [I

    fill-array-data v5, :array_f2

    invoke-direct {v3, v4, v5}, Landroid/graphics/drawable/GradientDrawable;-><init>(Landroid/graphics/drawable/GradientDrawable$Orientation;[I)V

    .line 834
    const/high16 v4, 0x41600000    # 14.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    int-to-float v4, v4

    invoke-virtual {v3, v4}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    .line 835
    invoke-virtual {v2, v3}, Landroid/widget/Button;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 836
    new-instance v3, Lcom/holy/dash/MainActivity$16;

    invoke-direct {v3, p0}, Lcom/holy/dash/MainActivity$16;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v2, v3}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 839
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v4, 0x435c0000    # 220.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    const/high16 v5, 0x42480000    # 50.0f

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-direct {v3, v4, v5}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 840
    const/high16 v4, 0x41b00000    # 22.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    iput v4, v3, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    .line 841
    invoke-virtual {v1, v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 842
    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    const/16 v3, 0x11

    invoke-direct {v2, v8, v8, v3}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    invoke-virtual {v0, v1, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 843
    iput-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    .line 844
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    new-instance v2, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v2, v9, v9}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v1, v0, v2}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 846
    :cond_d7
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v0, v6}, Landroid/view/View;->setVisibility(I)V

    .line 847
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->bringToFront()V

    .line 848
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    if-eqz v0, :cond_ec

    iget-object v0, p0, Lcom/holy/dash/MainActivity;->lockMsg:Landroid/widget/TextView;

    const-string v1, "\u0627\u0641\u062a\u062d \u0628\u0627\u0644\u0628\u0635\u0645\u0629 \u0644\u062a\u0631\u0649 \u0644\u0648\u062d\u062a\u0643"

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 849
    :cond_ec
    if-eqz p1, :cond_f1

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->askAuth()V

    .line 850
    :cond_f1
    return-void

    .line 833
    :array_f2
    .array-data 4
        -0xdd2c12
        -0x587406
    .end array-data
.end method

.method showSetup(Ljava/lang/String;)V
    .registers 12

    .prologue
    const/high16 v6, 0x41d00000    # 26.0f

    const/4 v9, -0x1

    const/4 v0, 0x1

    const/high16 v8, 0x41400000    # 12.0f

    const/4 v1, 0x0

    .line 248
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    if-nez v2, :cond_1f7

    .line 249
    new-instance v2, Landroid/widget/LinearLayout;

    invoke-direct {v2, p0}, Landroid/widget/LinearLayout;-><init>(Landroid/content/Context;)V

    .line 250
    invoke-virtual {v2, v0}, Landroid/widget/LinearLayout;->setOrientation(I)V

    .line 251
    invoke-virtual {v2, v0}, Landroid/widget/LinearLayout;->setGravity(I)V

    .line 252
    invoke-virtual {p0, v6}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v3

    const/high16 v4, 0x41f00000    # 30.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {p0, v6}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-virtual {p0, v6}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v6

    invoke-virtual {v2, v3, v4, v5, v6}, Landroid/widget/LinearLayout;->setPadding(IIII)V

    .line 253
    new-instance v3, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v3}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    .line 254
    const v4, -0xede9cd

    invoke-virtual {v3, v4}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    .line 255
    const/high16 v4, 0x41b00000    # 22.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    int-to-float v4, v4

    invoke-virtual {v3, v4}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    .line 256
    const/high16 v4, 0x3f800000    # 1.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    const v5, 0x33a78bfa

    invoke-virtual {v3, v4, v5}, Landroid/graphics/drawable/GradientDrawable;->setStroke(II)V

    .line 257
    invoke-virtual {v2, v3}, Landroid/widget/LinearLayout;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 258
    new-instance v3, Landroid/widget/ImageView;

    invoke-direct {v3, p0}, Landroid/widget/ImageView;-><init>(Landroid/content/Context;)V

    .line 259
    const/high16 v4, 0x7f020000

    invoke-virtual {v3, v4}, Landroid/widget/ImageView;->setImageResource(I)V

    .line 260
    new-instance v4, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v5, 0x42980000    # 76.0f

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    const/high16 v6, 0x42980000    # 76.0f

    invoke-virtual {p0, v6}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v6

    invoke-direct {v4, v5, v6}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v3, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 261
    const-string v3, "The Holy Dashboard"

    const/high16 v4, 0x41a80000    # 21.0f

    const v5, -0x131801

    invoke-virtual {p0, v3, v4, v5, v0}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v3

    .line 262
    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    const/high16 v5, 0x40800000    # 4.0f

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-virtual {v3, v1, v4, v1, v5}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 263
    invoke-virtual {v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 264
    const-string v3, "\u0627\u0643\u062a\u0628 \u0639\u0646\u0648\u0627\u0646 \u0644\u0648\u062d\u062a\u0643 (\u0646\u0641\u0633 \u0627\u0644\u0630\u064a \u062a\u0641\u062a\u062d\u0647 \u0641\u064a \u0627\u0644\u0645\u062a\u0635\u0641\u062d)"

    const/high16 v4, 0x41500000    # 13.0f

    const v5, -0x646c37

    invoke-virtual {p0, v3, v4, v5, v1}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v3

    invoke-virtual {v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 265
    new-instance v3, Landroid/widget/EditText;

    invoke-direct {v3, p0}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    iput-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    .line 266
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const-string v4, "http://1.2.3.4:8099"

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setHint(Ljava/lang/CharSequence;)V

    .line 267
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v3, v0}, Landroid/widget/EditText;->setSingleLine(Z)V

    .line 268
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const/16 v4, 0x11

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setInputType(I)V

    .line 269
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const/4 v4, 0x2

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setImeOptions(I)V

    .line 270
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const/4 v4, 0x3

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setTextDirection(I)V

    .line 271
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v3, v1}, Landroid/widget/EditText;->setLayoutDirection(I)V

    .line 272
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const/16 v4, 0x11

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setGravity(I)V

    .line 273
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const v4, -0x131801

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setTextColor(I)V

    .line 274
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const v4, -0x909862

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setHintTextColor(I)V

    .line 275
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    const/4 v4, 0x2

    const/high16 v5, 0x41800000    # 16.0f

    invoke-virtual {v3, v4, v5}, Landroid/widget/EditText;->setTextSize(IF)V

    .line 276
    new-instance v3, Landroid/graphics/drawable/GradientDrawable;

    invoke-direct {v3}, Landroid/graphics/drawable/GradientDrawable;-><init>()V

    .line 277
    const v4, -0xf4f1dc

    invoke-virtual {v3, v4}, Landroid/graphics/drawable/GradientDrawable;->setColor(I)V

    .line 278
    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    int-to-float v4, v4

    invoke-virtual {v3, v4}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    .line 279
    const/high16 v4, 0x3f800000    # 1.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    const v5, 0x5522d3ee

    invoke-virtual {v3, v4, v5}, Landroid/graphics/drawable/GradientDrawable;->setStroke(II)V

    .line 280
    iget-object v4, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v4, v3}, Landroid/widget/EditText;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 281
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v6

    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v7

    invoke-virtual {v3, v4, v5, v6, v7}, Landroid/widget/EditText;->setPadding(IIII)V

    .line 282
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    new-instance v4, Lcom/holy/dash/MainActivity$5;

    invoke-direct {v4, p0}, Lcom/holy/dash/MainActivity$5;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v3, v4}, Landroid/widget/EditText;->setOnEditorActionListener(Landroid/widget/TextView$OnEditorActionListener;)V

    .line 285
    new-instance v3, Landroid/widget/LinearLayout$LayoutParams;

    const/4 v4, -0x2

    invoke-direct {v3, v9, v4}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 286
    const/high16 v4, 0x41900000    # 18.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    iput v4, v3, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    .line 287
    iget-object v4, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v2, v4, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 288
    new-instance v3, Landroid/widget/Button;

    invoke-direct {v3, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 289
    const-string v4, "\u0627\u062a\u0635\u0627\u0644"

    invoke-virtual {v3, v4}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 290
    invoke-virtual {v3, v1}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 291
    const v4, -0xf7eee4

    invoke-virtual {v3, v4}, Landroid/widget/Button;->setTextColor(I)V

    .line 292
    sget-object v4, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    invoke-virtual {v3, v4}, Landroid/widget/Button;->setTypeface(Landroid/graphics/Typeface;)V

    .line 293
    new-instance v4, Landroid/graphics/drawable/GradientDrawable;

    sget-object v5, Landroid/graphics/drawable/GradientDrawable$Orientation;->LEFT_RIGHT:Landroid/graphics/drawable/GradientDrawable$Orientation;

    const/4 v6, 0x2

    new-array v6, v6, [I

    fill-array-data v6, :array_226

    invoke-direct {v4, v5, v6}, Landroid/graphics/drawable/GradientDrawable;-><init>(Landroid/graphics/drawable/GradientDrawable$Orientation;[I)V

    .line 294
    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    int-to-float v5, v5

    invoke-virtual {v4, v5}, Landroid/graphics/drawable/GradientDrawable;->setCornerRadius(F)V

    .line 295
    invoke-virtual {v3, v4}, Landroid/widget/Button;->setBackground(Landroid/graphics/drawable/Drawable;)V

    .line 296
    new-instance v4, Lcom/holy/dash/MainActivity$6;

    invoke-direct {v4, p0}, Lcom/holy/dash/MainActivity$6;-><init>(Lcom/holy/dash/MainActivity;)V

    invoke-virtual {v3, v4}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 299
    new-instance v4, Landroid/widget/LinearLayout$LayoutParams;

    const/high16 v5, 0x42480000    # 50.0f

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-direct {v4, v9, v5}, Landroid/widget/LinearLayout$LayoutParams;-><init>(II)V

    .line 300
    invoke-virtual {p0, v8}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    iput v5, v4, Landroid/widget/LinearLayout$LayoutParams;->topMargin:I

    .line 301
    invoke-virtual {v2, v3, v4}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 302
    const-string v3, ""

    const/high16 v4, 0x41480000    # 12.5f

    const v5, -0x48e7b

    invoke-virtual {p0, v3, v4, v5, v1}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v3

    iput-object v3, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    .line 303
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const/high16 v4, 0x41200000    # 10.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {v3, v1, v4, v1, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 304
    iget-object v3, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    invoke-virtual {v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 305
    const-string v3, "\u0628\u0639\u062f \u0627\u0644\u0627\u062a\u0635\u0627\u0644 \u0627\u062f\u062e\u0644 \u0628\u0643\u0644\u0645\u0629 \u0627\u0644\u0633\u0631 \u2014 \u0648\u062a\u064f\u0631\u0628\u0637 \u0627\u0644\u0625\u0634\u0639\u0627\u0631\u0627\u062a \u062a\u0644\u0642\u0627\u0626\u064a\u0627\u064b."

    const/high16 v4, 0x41380000    # 11.5f

    const v5, -0x909862

    invoke-virtual {p0, v3, v4, v5, v1}, Lcom/holy/dash/MainActivity;->text(Ljava/lang/String;FIZ)Landroid/widget/TextView;

    move-result-object v3

    .line 306
    const/high16 v4, 0x41000000    # 8.0f

    invoke-virtual {p0, v4}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v4

    invoke-virtual {v3, v1, v4, v1, v1}, Landroid/widget/TextView;->setPadding(IIII)V

    .line 307
    invoke-virtual {v2, v3}, Landroid/widget/LinearLayout;->addView(Landroid/view/View;)V

    .line 308
    new-instance v3, Landroid/widget/FrameLayout;

    invoke-direct {v3, p0}, Landroid/widget/FrameLayout;-><init>(Landroid/content/Context;)V

    .line 309
    new-instance v4, Landroid/widget/FrameLayout$LayoutParams;

    const/high16 v5, 0x43d20000    # 420.0f

    invoke-virtual {p0, v5}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v5

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->getResources()Landroid/content/res/Resources;

    move-result-object v6

    invoke-virtual {v6}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object v6

    iget v6, v6, Landroid/util/DisplayMetrics;->widthPixels:I

    const/high16 v7, 0x42000000    # 32.0f

    invoke-virtual {p0, v7}, Lcom/holy/dash/MainActivity;->dp(F)I

    move-result v7

    sub-int/2addr v6, v7

    invoke-static {v5, v6}, Ljava/lang/Math;->min(II)I

    move-result v5

    const/4 v6, -0x2

    const/16 v7, 0x11

    invoke-direct {v4, v5, v6, v7}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    .line 311
    invoke-virtual {v3, v2, v4}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 312
    iget v2, p0, Lcom/holy/dash/MainActivity;->bg:I

    invoke-virtual {v3, v2}, Landroid/widget/FrameLayout;->setBackgroundColor(I)V

    .line 313
    invoke-virtual {v3, v0}, Landroid/widget/FrameLayout;->setClickable(Z)V

    .line 314
    iput-object v3, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    .line 315
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->root:Landroid/widget/FrameLayout;

    iget-object v3, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    new-instance v4, Landroid/widget/FrameLayout$LayoutParams;

    invoke-direct {v4, v9, v9}, Landroid/widget/FrameLayout$LayoutParams;-><init>(II)V

    invoke-virtual {v2, v3, v4}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 317
    :cond_1f7
    if-eqz p1, :cond_220

    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-nez v2, :cond_220

    .line 318
    :goto_1ff
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->urlField:Landroid/widget/EditText;

    invoke-virtual {v2, p1}, Landroid/widget/EditText;->setText(Ljava/lang/CharSequence;)V

    .line 319
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->setupMsg:Landroid/widget/TextView;

    const-string v3, ""

    invoke-virtual {v2, v3}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 320
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    invoke-virtual {v2, v1}, Landroid/view/View;->setVisibility(I)V

    .line 321
    iget-object v2, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    invoke-virtual {v2}, Landroid/view/View;->bringToFront()V

    .line 322
    if-eqz p1, :cond_223

    invoke-virtual {p1}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-nez v2, :cond_223

    :goto_21d
    iput-boolean v0, p0, Lcom/holy/dash/MainActivity;->clipTried:Z

    .line 323
    return-void

    .line 317
    :cond_220
    iget-object p1, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    goto :goto_1ff

    :cond_223
    move v0, v1

    .line 322
    goto :goto_21d

    .line 293
    nop

    :array_226
    .array-data 4
        -0xdd2c12
        -0x74a30a
    .end array-data
.end method

.method text(Ljava/lang/String;FIZ)Landroid/widget/TextView;
    .registers 7

    .prologue
    .line 326
    new-instance v0, Landroid/widget/TextView;

    invoke-direct {v0, p0}, Landroid/widget/TextView;-><init>(Landroid/content/Context;)V

    .line 327
    invoke-virtual {v0, p1}, Landroid/widget/TextView;->setText(Ljava/lang/CharSequence;)V

    .line 328
    const/4 v1, 0x2

    invoke-virtual {v0, v1, p2}, Landroid/widget/TextView;->setTextSize(IF)V

    .line 329
    invoke-virtual {v0, p3}, Landroid/widget/TextView;->setTextColor(I)V

    .line 330
    const/16 v1, 0x11

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setGravity(I)V

    .line 331
    if-eqz p4, :cond_1b

    sget-object v1, Landroid/graphics/Typeface;->DEFAULT_BOLD:Landroid/graphics/Typeface;

    invoke-virtual {v0, v1}, Landroid/widget/TextView;->setTypeface(Landroid/graphics/Typeface;)V

    .line 332
    :cond_1b
    return-object v0
.end method

.method useOrigin(Ljava/lang/String;)V
    .registers 5

    .prologue
    .line 389
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_2b

    const/4 v0, 0x1

    .line 390
    :goto_9
    if-eqz v0, :cond_14

    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v1

    if-eqz v1, :cond_14

    invoke-static {p0}, Lcom/holy/dash/WatchService;->stop(Landroid/content/Context;)V

    .line 391
    :cond_14
    invoke-static {p0, p1}, Lcom/holy/dash/Prefs;->setOrigin(Landroid/content/Context;Ljava/lang/String;)V

    .line 392
    iput-object p1, p0, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    .line 393
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->setup:Landroid/view/View;

    const/16 v2, 0x8

    invoke-virtual {v1, v2}, Landroid/view/View;->setVisibility(I)V

    .line 394
    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->hideKeyboard()V

    .line 395
    iget-object v1, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    if-nez v1, :cond_2d

    invoke-virtual {p0}, Lcom/holy/dash/MainActivity;->openDashboard()V

    .line 397
    :cond_2a
    :goto_2a
    return-void

    .line 389
    :cond_2b
    const/4 v0, 0x0

    goto :goto_9

    .line 396
    :cond_2d
    if-nez v0, :cond_33

    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->pageReady:Z

    if-nez v0, :cond_2a

    :cond_33
    iget-object v0, p0, Lcom/holy/dash/MainActivity;->web:Landroid/webkit/WebView;

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, "/"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/webkit/WebView;->loadUrl(Ljava/lang/String;)V

    goto :goto_2a
.end method

.method webViewTooOld()V
    .registers 5

    .prologue
    const/4 v1, 0x1

    .line 554
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity;->oldWarned:Z

    if-eqz v0, :cond_6

    .line 578
    :cond_5
    :goto_5
    return-void

    .line 555
    :cond_6
    iput-boolean v1, p0, Lcom/holy/dash/MainActivity;->oldWarned:Z

    .line 556
    const/4 v0, 0x0

    .line 558
    :try_start_9
    const-string v1, "Chrome/(\\d+)"

    invoke-static {v1}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;

    move-result-object v1

    invoke-static {p0}, Landroid/webkit/WebSettings;->getDefaultUserAgent(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1, v2}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v1

    .line 559
    invoke-virtual {v1}, Ljava/util/regex/Matcher;->find()Z

    move-result v2

    if-eqz v2, :cond_26

    const/4 v0, 0x1

    invoke-virtual {v1, v0}, Ljava/util/regex/Matcher;->group(I)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Ljava/lang/Integer;->parseInt(Ljava/lang/String;)I
    :try_end_25
    .catch Ljava/lang/Exception; {:try_start_9 .. :try_end_25} :catch_6d

    move-result v0

    .line 563
    :cond_26
    if-eqz v0, :cond_5

    const/16 v1, 0x50

    if-ge v0, v1, :cond_5

    .line 564
    new-instance v1, Landroid/app/AlertDialog$Builder;

    const v2, 0x10302d1

    invoke-direct {v1, p0, v2}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "\u26a0\ufe0f \u0645\u062a\u0635\u0641\u062d \u0627\u0644\u0646\u0638\u0627\u0645 \u0642\u062f\u064a\u0645 (Chrome "

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v2, ")"

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v1, v0}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u062a\u062d\u062a\u0627\u062c \u0627\u0644\u0644\u0648\u062d\u0629 \u00abAndroid System WebView\u00bb \u0623\u062d\u062f\u062b \u0644\u062a\u0639\u0645\u0644 \u0623\u0632\u0631\u0627\u0631\u0647\u0627 \u0648\u0623\u0631\u0642\u0627\u0645\u0647\u0627 \u2014 \u062d\u062f\u0651\u062b\u0647 \u0645\u0646 \u0627\u0644\u0645\u062a\u062c\u0631 \u062b\u0645 \u0627\u0641\u062a\u062d Holy \u0645\u0646 \u062c\u062f\u064a\u062f."

    .line 565
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u062d\u062f\u0651\u062b\u0647 \u0645\u0646 \u0627\u0644\u0645\u062a\u062c\u0631"

    new-instance v2, Lcom/holy/dash/MainActivity$9;

    invoke-direct {v2, p0}, Lcom/holy/dash/MainActivity$9;-><init>(Lcom/holy/dash/MainActivity;)V

    .line 566
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0644\u0627\u062d\u0642\u0627\u064b"

    const/4 v2, 0x0

    .line 577
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    goto :goto_5

    .line 560
    :catch_6d
    move-exception v0

    goto :goto_5
.end method
