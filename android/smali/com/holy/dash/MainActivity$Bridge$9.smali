.class Lcom/holy/dash/MainActivity$Bridge$9;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->setFps(I)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Bridge;

.field final synthetic val$hz:I


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;I)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 1207
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$9;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iput p2, p0, Lcom/holy/dash/MainActivity$Bridge$9;->val$hz:I

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 5

    .prologue
    .line 1209
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$9;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget v1, p0, Lcom/holy/dash/MainActivity$Bridge$9;->val$hz:I

    invoke-static {v0, v1}, Lcom/holy/dash/Hz;->apply(Landroid/app/Activity;I)I

    .line 1210
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$9;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->ui:Landroid/os/Handler;

    new-instance v1, Lcom/holy/dash/MainActivity$Bridge$9$1;

    invoke-direct {v1, p0}, Lcom/holy/dash/MainActivity$Bridge$9$1;-><init>(Lcom/holy/dash/MainActivity$Bridge$9;)V

    const-wide/16 v2, 0x258

    invoke-virtual {v0, v1, v2, v3}, Landroid/os/Handler;->postDelayed(Ljava/lang/Runnable;J)Z

    .line 1211
    return-void
.end method
