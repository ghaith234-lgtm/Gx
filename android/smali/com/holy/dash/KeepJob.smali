.class public Lcom/holy/dash/KeepJob;
.super Landroid/app/job/JobService;
.source "KeepJob.java"


# direct methods
.method public constructor <init>()V
    .registers 1

    .prologue
    .line 10
    invoke-direct {p0}, Landroid/app/job/JobService;-><init>()V

    return-void
.end method


# virtual methods
.method public onStartJob(Landroid/app/job/JobParameters;)Z
    .registers 5

    .prologue
    const/4 v0, 0x0

    .line 13
    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v1

    if-eqz v1, :cond_d

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v1

    if-nez v1, :cond_11

    .line 14
    :cond_d
    invoke-static {p0}, Lcom/holy/dash/Keep;->cancel(Landroid/content/Context;)V

    .line 32
    :cond_10
    :goto_10
    return v0

    .line 17
    :cond_11
    sget-boolean v1, Lcom/holy/dash/WatchService;->RUNNING:Z

    if-nez v1, :cond_10

    .line 18
    invoke-static {p0}, Lcom/holy/dash/WatchService;->start(Landroid/content/Context;)V

    .line 19
    new-instance v0, Ljava/lang/Thread;

    new-instance v1, Lcom/holy/dash/KeepJob$1;

    invoke-direct {v1, p0, p1}, Lcom/holy/dash/KeepJob$1;-><init>(Lcom/holy/dash/KeepJob;Landroid/app/job/JobParameters;)V

    const-string v2, "holy-keepjob"

    invoke-direct {v0, v1, v2}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 31
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V

    .line 32
    const/4 v0, 0x1

    goto :goto_10
.end method

.method public onStopJob(Landroid/app/job/JobParameters;)Z
    .registers 3

    .prologue
    .line 36
    const/4 v0, 0x0

    return v0
.end method
