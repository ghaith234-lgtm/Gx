.class final Lcom/holy/dash/MainActivity$Client;
.super Landroid/webkit/WebViewClient;
.source "MainActivity.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/holy/dash/MainActivity;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x10
    name = "Client"
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 446
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Landroid/webkit/WebViewClient;-><init>()V

    return-void
.end method


# virtual methods
.method public onPageFinished(Landroid/webkit/WebView;Ljava/lang/String;)V
    .registers 6

    .prologue
    const/4 v2, 0x0

    .line 467
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x1

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->pageReady:Z

    .line 468
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    iget-boolean v0, v0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    if-eqz v0, :cond_15

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    iput-boolean v2, v0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->hideLock()V

    .line 469
    :cond_15
    invoke-static {}, Landroid/webkit/CookieManager;->getInstance()Landroid/webkit/CookieManager;

    move-result-object v0

    invoke-virtual {v0}, Landroid/webkit/CookieManager;->flush()V

    .line 470
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    if-eqz v0, :cond_2b

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    const/16 v1, 0x8

    invoke-virtual {v0, v1}, Landroid/widget/ProgressBar;->setVisibility(I)V

    .line 471
    :cond_2b
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    iget-boolean v0, v0, Lcom/holy/dash/MainActivity;->errShown:Z

    if-nez v0, :cond_3c

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->pendingGo:Ljava/lang/String;

    if-eqz v0, :cond_3c

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->runGo()V

    .line 472
    :cond_3c
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0, v2}, Lcom/holy/dash/Updater;->check(Landroid/app/Activity;Z)V

    .line 473
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->webViewTooOld()V

    .line 474
    return-void
.end method

.method public onPageStarted(Landroid/webkit/WebView;Ljava/lang/String;Landroid/graphics/Bitmap;)V
    .registers 6

    .prologue
    .line 461
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {p2}, Lcom/holy/dash/Net;->originOf(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    iput-object v1, v0, Lcom/holy/dash/MainActivity;->pageOrigin:Ljava/lang/String;

    .line 462
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->pageReady:Z

    .line 463
    return-void
.end method

.method public onReceivedError(Landroid/webkit/WebView;Landroid/webkit/WebResourceRequest;Landroid/webkit/WebResourceError;)V
    .registers 6

    .prologue
    .line 478
    invoke-interface {p2}, Landroid/webkit/WebResourceRequest;->isForMainFrame()Z

    move-result v0

    if-eqz v0, :cond_13

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {p3}, Landroid/webkit/WebResourceError;->getDescription()Ljava/lang/CharSequence;

    move-result-object v1

    invoke-static {v1}, Ljava/lang/String;->valueOf(Ljava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->showError(Ljava/lang/String;)V

    .line 479
    :cond_13
    return-void
.end method

.method public shouldOverrideUrlLoading(Landroid/webkit/WebView;Landroid/webkit/WebResourceRequest;)Z
    .registers 7

    .prologue
    .line 449
    invoke-interface {p2}, Landroid/webkit/WebResourceRequest;->getUrl()Landroid/net/Uri;

    move-result-object v0

    .line 450
    iget-object v1, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v1, v0}, Lcom/holy/dash/MainActivity;->ours(Landroid/net/Uri;)Z

    move-result v1

    if-eqz v1, :cond_e

    const/4 v0, 0x0

    .line 456
    :goto_d
    return v0

    .line 452
    :cond_e
    :try_start_e
    iget-object v1, p0, Lcom/holy/dash/MainActivity$Client;->this$0:Lcom/holy/dash/MainActivity;

    new-instance v2, Landroid/content/Intent;

    const-string v3, "android.intent.action.VIEW"

    invoke-direct {v2, v3, v0}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V

    const/high16 v0, 0x10000000

    invoke-virtual {v2, v0}, Landroid/content/Intent;->addFlags(I)Landroid/content/Intent;

    move-result-object v0

    invoke-virtual {v1, v0}, Lcom/holy/dash/MainActivity;->startActivity(Landroid/content/Intent;)V
    :try_end_20
    .catch Ljava/lang/Exception; {:try_start_e .. :try_end_20} :catch_22

    .line 456
    :goto_20
    const/4 v0, 0x1

    goto :goto_d

    .line 453
    :catch_22
    move-exception v0

    goto :goto_20
.end method
