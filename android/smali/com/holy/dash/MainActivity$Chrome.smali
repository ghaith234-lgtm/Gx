.class final Lcom/holy/dash/MainActivity$Chrome;
.super Landroid/webkit/WebChromeClient;
.source "MainActivity.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/holy/dash/MainActivity;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x10
    name = "Chrome"
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 482
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Landroid/webkit/WebChromeClient;-><init>()V

    return-void
.end method


# virtual methods
.method public onJsAlert(Landroid/webkit/WebView;Ljava/lang/String;Ljava/lang/String;Landroid/webkit/JsResult;)Z
    .registers 8

    .prologue
    .line 506
    new-instance v0, Landroid/app/AlertDialog$Builder;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    const v2, 0x10302d1

    invoke-direct {v0, v1, v2}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    invoke-virtual {v0, p3}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u062d\u0633\u0646\u0627\u064b"

    new-instance v2, Lcom/holy/dash/MainActivity$Chrome$2;

    invoke-direct {v2, p0, p4}, Lcom/holy/dash/MainActivity$Chrome$2;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsResult;)V

    .line 507
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lcom/holy/dash/MainActivity$Chrome$1;

    invoke-direct {v1, p0, p4}, Lcom/holy/dash/MainActivity$Chrome$1;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsResult;)V

    .line 510
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setOnCancelListener(Landroid/content/DialogInterface$OnCancelListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 512
    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 513
    const/4 v0, 0x1

    return v0
.end method

.method public onJsConfirm(Landroid/webkit/WebView;Ljava/lang/String;Ljava/lang/String;Landroid/webkit/JsResult;)Z
    .registers 8

    .prologue
    .line 518
    new-instance v0, Landroid/app/AlertDialog$Builder;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    const v2, 0x10302d1

    invoke-direct {v0, v1, v2}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    invoke-virtual {v0, p3}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u062a\u0623\u0643\u064a\u062f"

    new-instance v2, Lcom/holy/dash/MainActivity$Chrome$5;

    invoke-direct {v2, p0, p4}, Lcom/holy/dash/MainActivity$Chrome$5;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsResult;)V

    .line 519
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0625\u0644\u063a\u0627\u0621"

    new-instance v2, Lcom/holy/dash/MainActivity$Chrome$4;

    invoke-direct {v2, p0, p4}, Lcom/holy/dash/MainActivity$Chrome$4;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsResult;)V

    .line 522
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lcom/holy/dash/MainActivity$Chrome$3;

    invoke-direct {v1, p0, p4}, Lcom/holy/dash/MainActivity$Chrome$3;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsResult;)V

    .line 525
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setOnCancelListener(Landroid/content/DialogInterface$OnCancelListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 527
    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 528
    const/4 v0, 0x1

    return v0
.end method

.method public onJsPrompt(Landroid/webkit/WebView;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Landroid/webkit/JsPromptResult;)Z
    .registers 11

    .prologue
    const/4 v4, 0x1

    .line 533
    new-instance v0, Landroid/widget/EditText;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {v0, v1}, Landroid/widget/EditText;-><init>(Landroid/content/Context;)V

    .line 534
    invoke-virtual {v0, p4}, Landroid/widget/EditText;->setText(Ljava/lang/CharSequence;)V

    .line 535
    invoke-virtual {v0, v4}, Landroid/widget/EditText;->setSingleLine(Z)V

    .line 536
    new-instance v1, Landroid/app/AlertDialog$Builder;

    iget-object v2, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    const v3, 0x10302d1

    invoke-direct {v1, v2, v3}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;I)V

    invoke-virtual {v1, p3}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    invoke-virtual {v1, v0}, Landroid/app/AlertDialog$Builder;->setView(Landroid/view/View;)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    const-string v2, "\u062d\u0633\u0646\u0627\u064b"

    new-instance v3, Lcom/holy/dash/MainActivity$Chrome$8;

    invoke-direct {v3, p0, p5, v0}, Lcom/holy/dash/MainActivity$Chrome$8;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsPromptResult;Landroid/widget/EditText;)V

    .line 537
    invoke-virtual {v1, v2, v3}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    const-string v1, "\u0625\u0644\u063a\u0627\u0621"

    new-instance v2, Lcom/holy/dash/MainActivity$Chrome$7;

    invoke-direct {v2, p0, p5}, Lcom/holy/dash/MainActivity$Chrome$7;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsPromptResult;)V

    .line 540
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    new-instance v1, Lcom/holy/dash/MainActivity$Chrome$6;

    invoke-direct {v1, p0, p5}, Lcom/holy/dash/MainActivity$Chrome$6;-><init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsPromptResult;)V

    .line 543
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setOnCancelListener(Landroid/content/DialogInterface$OnCancelListener;)Landroid/app/AlertDialog$Builder;

    move-result-object v0

    .line 545
    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 546
    return v4
.end method

.method public onProgressChanged(Landroid/webkit/WebView;I)V
    .registers 5

    .prologue
    .line 485
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    if-nez v0, :cond_7

    .line 488
    :goto_6
    return-void

    .line 486
    :cond_7
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    invoke-virtual {v0, p2}, Landroid/widget/ProgressBar;->setProgress(I)V

    .line 487
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v0, Lcom/holy/dash/MainActivity;->bar:Landroid/widget/ProgressBar;

    const/16 v0, 0x64

    if-lt p2, v0, :cond_1c

    const/16 v0, 0x8

    :goto_18
    invoke-virtual {v1, v0}, Landroid/widget/ProgressBar;->setVisibility(I)V

    goto :goto_6

    :cond_1c
    const/4 v0, 0x0

    goto :goto_18
.end method

.method public onShowFileChooser(Landroid/webkit/WebView;Landroid/webkit/ValueCallback;Landroid/webkit/WebChromeClient$FileChooserParams;)Z
    .registers 8
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroid/webkit/WebView;",
            "Landroid/webkit/ValueCallback",
            "<[",
            "Landroid/net/Uri;",
            ">;",
            "Landroid/webkit/WebChromeClient$FileChooserParams;",
            ")Z"
        }
    .end annotation

    .prologue
    const/4 v3, 0x0

    .line 492
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    if-eqz v0, :cond_e

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    invoke-interface {v0, v3}, Landroid/webkit/ValueCallback;->onReceiveValue(Ljava/lang/Object;)V

    .line 493
    :cond_e
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iput-object p2, v0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    .line 495
    :try_start_12
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {p3}, Landroid/webkit/WebChromeClient$FileChooserParams;->createIntent()Landroid/content/Intent;

    move-result-object v1

    const/16 v2, 0xd

    invoke-virtual {v0, v1, v2}, Lcom/holy/dash/MainActivity;->startActivityForResult(Landroid/content/Intent;I)V
    :try_end_1d
    .catch Ljava/lang/Exception; {:try_start_12 .. :try_end_1d} :catch_1f

    .line 500
    const/4 v0, 0x1

    :goto_1e
    return v0

    .line 496
    :catch_1f
    move-exception v0

    .line 497
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome;->this$0:Lcom/holy/dash/MainActivity;

    iput-object v3, v0, Lcom/holy/dash/MainActivity;->fileCb:Landroid/webkit/ValueCallback;

    .line 498
    const/4 v0, 0x0

    goto :goto_1e
.end method
