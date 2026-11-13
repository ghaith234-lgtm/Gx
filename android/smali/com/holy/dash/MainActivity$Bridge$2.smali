.class Lcom/holy/dash/MainActivity$Bridge$2;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->setWatch(Z)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Bridge;

.field final synthetic val$on:Z


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;Z)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 1125
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$2;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iput-boolean p2, p0, Lcom/holy/dash/MainActivity$Bridge$2;->val$on:Z

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 2

    .prologue
    .line 1127
    iget-boolean v0, p0, Lcom/holy/dash/MainActivity$Bridge$2;->val$on:Z

    if-eqz v0, :cond_c

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$2;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/WatchService;->start(Landroid/content/Context;)V

    .line 1129
    :goto_b
    return-void

    .line 1128
    :cond_c
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$2;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/WatchService;->stop(Landroid/content/Context;)V

    goto :goto_b
.end method
