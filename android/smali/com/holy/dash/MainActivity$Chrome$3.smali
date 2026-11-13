.class Lcom/holy/dash/MainActivity$Chrome$3;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/content/DialogInterface$OnCancelListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Chrome;->onJsConfirm(Landroid/webkit/WebView;Ljava/lang/String;Ljava/lang/String;Landroid/webkit/JsResult;)Z
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Chrome;

.field final synthetic val$r:Landroid/webkit/JsResult;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Chrome;Landroid/webkit/JsResult;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 525
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Chrome$3;->this$1:Lcom/holy/dash/MainActivity$Chrome;

    iput-object p2, p0, Lcom/holy/dash/MainActivity$Chrome$3;->val$r:Landroid/webkit/JsResult;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onCancel(Landroid/content/DialogInterface;)V
    .registers 3

    .prologue
    .line 526
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Chrome$3;->val$r:Landroid/webkit/JsResult;

    invoke-virtual {v0}, Landroid/webkit/JsResult;->cancel()V

    return-void
.end method
