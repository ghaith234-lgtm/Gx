.class Lcom/holy/dash/MainActivity$Chrome$8;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Chrome;->onJsPrompt(Landroid/webkit/WebView;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Landroid/webkit/JsPromptResult;)Z
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Chrome;

.field final synthetic val$in:Landroid/widget/EditText;

.field final synthetic val$r:Landroid/webkit/JsPromptResult;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsPromptResult;Landroid/widget/EditText;)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 537
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Chrome$8;->this$1:Lcom/holy/dash/MainActivity$Chrome;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$Chrome$8;->val$r:Landroid/webkit/JsPromptResult;

    iput-object p3, p0, Lcom/holy/dash/MainActivity$Chrome$8;->val$in:Landroid/widget/EditText;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 5

    .prologue
    .line 538
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome$8;->val$r:Landroid/webkit/JsPromptResult;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Chrome$8;->val$in:Landroid/widget/EditText;

    invoke-virtual {v1}, Landroid/widget/EditText;->getText()Landroid/text/Editable;

    move-result-object v1

    invoke-interface {v1}, Landroid/text/Editable;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/webkit/JsPromptResult;->confirm(Ljava/lang/String;)V

    return-void
.end method
