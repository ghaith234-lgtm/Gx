.class Lcom/holy/dash/KeepJob$1;
.super Ljava/lang/Object;
.source "KeepJob.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/KeepJob;->onStartJob(Landroid/app/job/JobParameters;)Z
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/KeepJob;

.field final synthetic val$p:Landroid/app/job/JobParameters;


# direct methods
.method constructor <init>(Lcom/holy/dash/KeepJob;Landroid/app/job/JobParameters;)V
    .registers 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()V"
        }
    .end annotation

    .prologue
    .line 19
    iput-object p1, p0, Lcom/holy/dash/KeepJob$1;->this$0:Lcom/holy/dash/KeepJob;

    iput-object p2, p0, Lcom/holy/dash/KeepJob$1;->val$p:Landroid/app/job/JobParameters;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 5

    .prologue
    const/4 v3, 0x0

    .line 22
    const-wide/16 v0, 0xbb8

    :try_start_3
    invoke-static {v0, v1}, Ljava/lang/Thread;->sleep(J)V

    .line 23
    sget-boolean v0, Lcom/holy/dash/WatchService;->RUNNING:Z

    if-nez v0, :cond_f

    iget-object v0, p0, Lcom/holy/dash/KeepJob$1;->this$0:Lcom/holy/dash/KeepJob;

    invoke-static {v0}, Lcom/holy/dash/Feed;->pollOnce(Landroid/content/Context;)I

    .line 24
    :cond_f
    iget-object v0, p0, Lcom/holy/dash/KeepJob$1;->this$0:Lcom/holy/dash/KeepJob;

    invoke-static {v0}, Lcom/holy/dash/HolyWidget;->tick(Landroid/content/Context;)V
    :try_end_14
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_14} :catch_1c
    .catchall {:try_start_3 .. :try_end_14} :catchall_25

    .line 28
    iget-object v0, p0, Lcom/holy/dash/KeepJob$1;->this$0:Lcom/holy/dash/KeepJob;

    iget-object v1, p0, Lcom/holy/dash/KeepJob$1;->val$p:Landroid/app/job/JobParameters;

    invoke-virtual {v0, v1, v3}, Lcom/holy/dash/KeepJob;->jobFinished(Landroid/app/job/JobParameters;Z)V

    .line 30
    :goto_1b
    return-void

    .line 25
    :catch_1c
    move-exception v0

    .line 28
    iget-object v0, p0, Lcom/holy/dash/KeepJob$1;->this$0:Lcom/holy/dash/KeepJob;

    iget-object v1, p0, Lcom/holy/dash/KeepJob$1;->val$p:Landroid/app/job/JobParameters;

    invoke-virtual {v0, v1, v3}, Lcom/holy/dash/KeepJob;->jobFinished(Landroid/app/job/JobParameters;Z)V

    goto :goto_1b

    :catchall_25
    move-exception v0

    iget-object v1, p0, Lcom/holy/dash/KeepJob$1;->this$0:Lcom/holy/dash/KeepJob;

    iget-object v2, p0, Lcom/holy/dash/KeepJob$1;->val$p:Landroid/app/job/JobParameters;

    invoke-virtual {v1, v2, v3}, Lcom/holy/dash/KeepJob;->jobFinished(Landroid/app/job/JobParameters;Z)V

    .line 29
    throw v0
.end method
