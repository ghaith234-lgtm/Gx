.class Lcom/holy/dash/Keep$1;
.super Ljava/lang/Object;
.source "Keep.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/Keep;->onReceive(Landroid/content/Context;Landroid/content/Intent;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/Keep;

.field final synthetic val$c:Landroid/content/Context;

.field final synthetic val$pr:Landroid/content/BroadcastReceiver$PendingResult;


# direct methods
.method constructor <init>(Lcom/holy/dash/Keep;Landroid/content/Context;Landroid/content/BroadcastReceiver$PendingResult;)V
    .registers 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 70
    iput-object p1, p0, Lcom/holy/dash/Keep$1;->this$0:Lcom/holy/dash/Keep;

    iput-object p2, p0, Lcom/holy/dash/Keep$1;->val$c:Landroid/content/Context;

    iput-object p3, p0, Lcom/holy/dash/Keep$1;->val$pr:Landroid/content/BroadcastReceiver$PendingResult;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .prologue
    .line 73
    const-wide/16 v0, 0xbb8

    :try_start_2
    invoke-static {v0, v1}, Ljava/lang/Thread;->sleep(J)V

    .line 74
    sget-boolean v0, Lcom/holy/dash/WatchService;->RUNNING:Z

    if-nez v0, :cond_e

    iget-object v0, p0, Lcom/holy/dash/Keep$1;->val$c:Landroid/content/Context;

    invoke-static {v0}, Lcom/holy/dash/Feed;->pollOnce(Landroid/content/Context;)I
    :try_end_e
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_e} :catch_14
    .catchall {:try_start_2 .. :try_end_e} :catchall_1b

    .line 78
    :cond_e
    iget-object v0, p0, Lcom/holy/dash/Keep$1;->val$pr:Landroid/content/BroadcastReceiver$PendingResult;

    invoke-virtual {v0}, Landroid/content/BroadcastReceiver$PendingResult;->finish()V

    .line 80
    :goto_13
    return-void

    .line 75
    :catch_14
    move-exception v0

    .line 78
    iget-object v0, p0, Lcom/holy/dash/Keep$1;->val$pr:Landroid/content/BroadcastReceiver$PendingResult;

    invoke-virtual {v0}, Landroid/content/BroadcastReceiver$PendingResult;->finish()V

    goto :goto_13

    :catchall_1b
    move-exception v0

    iget-object v1, p0, Lcom/holy/dash/Keep$1;->val$pr:Landroid/content/BroadcastReceiver$PendingResult;

    invoke-virtual {v1}, Landroid/content/BroadcastReceiver$PendingResult;->finish()V

    .line 79
    throw v0
.end method
