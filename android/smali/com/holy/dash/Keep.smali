.class public Lcom/holy/dash/Keep;
.super Landroid/content/BroadcastReceiver;
.source "Keep.java"


# static fields
.field static final ACT:Ljava/lang/String; = "com.holy.dash.KEEP"

.field static final JOB_ID:I = 0x1c8f


# direct methods
.method public constructor <init>()V
    .registers 1

    .prologue
    .line 20
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method

.method static cancel(Landroid/content/Context;)V
    .registers 3

    .prologue
    .line 43
    :try_start_0
    const-string v0, "jobscheduler"

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/job/JobScheduler;

    .line 44
    if-eqz v0, :cond_f

    const/16 v1, 0x1c8f

    invoke-virtual {v0, v1}, Landroid/app/job/JobScheduler;->cancel(I)V
    :try_end_f
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_f} :catch_10

    .line 46
    :cond_f
    :goto_f
    return-void

    .line 45
    :catch_10
    move-exception v0

    goto :goto_f
.end method

.method static schedule(Landroid/content/Context;)V
    .registers 7

    .prologue
    const/16 v5, 0x18

    .line 25
    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_e

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_12

    :cond_e
    invoke-static {p0}, Lcom/holy/dash/Keep;->cancel(Landroid/content/Context;)V

    .line 39
    :cond_11
    :goto_11
    return-void

    .line 27
    :cond_12
    :try_start_12
    const-string v0, "jobscheduler"

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/job/JobScheduler;

    .line 28
    if-eqz v0, :cond_11

    .line 29
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v1, v5, :cond_28

    const/16 v1, 0x1c8f

    invoke-virtual {v0, v1}, Landroid/app/job/JobScheduler;->getPendingJob(I)Landroid/app/job/JobInfo;

    move-result-object v1

    if-nez v1, :cond_11

    .line 30
    :cond_28
    new-instance v1, Landroid/app/job/JobInfo$Builder;

    const/16 v2, 0x1c8f

    new-instance v3, Landroid/content/ComponentName;

    const-class v4, Lcom/holy/dash/KeepJob;

    invoke-direct {v3, p0, v4}, Landroid/content/ComponentName;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-direct {v1, v2, v3}, Landroid/app/job/JobInfo$Builder;-><init>(ILandroid/content/ComponentName;)V

    const/4 v2, 0x1

    .line 31
    invoke-virtual {v1, v2}, Landroid/app/job/JobInfo$Builder;->setRequiredNetworkType(I)Landroid/app/job/JobInfo$Builder;

    move-result-object v1

    const/4 v2, 0x1

    .line 32
    invoke-virtual {v1, v2}, Landroid/app/job/JobInfo$Builder;->setPersisted(Z)Landroid/app/job/JobInfo$Builder;

    move-result-object v1

    .line 33
    sget v2, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v2, v5, :cond_57

    const-wide/32 v2, 0xdbba0

    const-wide/32 v4, 0x493e0

    invoke-virtual {v1, v2, v3, v4, v5}, Landroid/app/job/JobInfo$Builder;->setPeriodic(JJ)Landroid/app/job/JobInfo$Builder;

    .line 35
    :goto_4d
    invoke-virtual {v1}, Landroid/app/job/JobInfo$Builder;->build()Landroid/app/job/JobInfo;

    move-result-object v1

    invoke-virtual {v0, v1}, Landroid/app/job/JobScheduler;->schedule(Landroid/app/job/JobInfo;)I

    goto :goto_11

    .line 36
    :catch_55
    move-exception v0

    goto :goto_11

    .line 34
    :cond_57
    const-wide/32 v2, 0xdbba0

    invoke-virtual {v1, v2, v3}, Landroid/app/job/JobInfo$Builder;->setPeriodic(J)Landroid/app/job/JobInfo$Builder;
    :try_end_5d
    .catch Ljava/lang/Exception; {:try_start_12 .. :try_end_5d} :catch_55

    goto :goto_4d
.end method

.method static soon(Landroid/content/Context;J)V
    .registers 10

    .prologue
    const/16 v5, 0x17

    .line 50
    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_e

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_f

    .line 62
    :cond_e
    :goto_e
    return-void

    .line 52
    :cond_f
    :try_start_f
    const-string v0, "alarm"

    invoke-virtual {p0, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/AlarmManager;

    .line 53
    new-instance v1, Landroid/content/Intent;

    const-class v2, Lcom/holy/dash/Keep;

    invoke-direct {v1, p0, v2}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const-string v2, "com.holy.dash.KEEP"

    invoke-virtual {v1, v2}, Landroid/content/Intent;->setAction(Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v2

    .line 54
    const/high16 v3, 0x8000000

    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v1, v5, :cond_43

    const/high16 v1, 0x4000000

    :goto_2c
    or-int/2addr v1, v3

    .line 55
    const/16 v3, 0x1c90

    invoke-static {p0, v3, v2, v1}, Landroid/app/PendingIntent;->getBroadcast(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v1

    .line 56
    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v2

    add-long/2addr v2, p1

    .line 57
    sget v4, Landroid/os/Build$VERSION;->SDK_INT:I

    if-lt v4, v5, :cond_45

    const/4 v4, 0x2

    invoke-virtual {v0, v4, v2, v3, v1}, Landroid/app/AlarmManager;->setAndAllowWhileIdle(IJLandroid/app/PendingIntent;)V

    goto :goto_e

    .line 59
    :catch_41
    move-exception v0

    goto :goto_e

    .line 54
    :cond_43
    const/4 v1, 0x0

    goto :goto_2c

    .line 58
    :cond_45
    const/4 v4, 0x2

    invoke-virtual {v0, v4, v2, v3, v1}, Landroid/app/AlarmManager;->set(IJLandroid/app/PendingIntent;)V
    :try_end_49
    .catch Ljava/lang/Exception; {:try_start_f .. :try_end_49} :catch_41

    goto :goto_e
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 6

    .prologue
    .line 66
    if-eqz p2, :cond_e

    const-string v0, "com.holy.dash.KEEP"

    invoke-virtual {p2}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object v1

    invoke-virtual {v0, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_f

    .line 82
    :cond_e
    :goto_e
    return-void

    .line 67
    :cond_f
    sget-boolean v0, Lcom/holy/dash/WatchService;->RUNNING:Z

    if-nez v0, :cond_e

    .line 68
    invoke-static {p1}, Lcom/holy/dash/WatchService;->start(Landroid/content/Context;)V

    .line 69
    invoke-virtual {p0}, Lcom/holy/dash/Keep;->goAsync()Landroid/content/BroadcastReceiver$PendingResult;

    move-result-object v0

    .line 70
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/holy/dash/Keep$1;

    invoke-direct {v2, p0, p1, v0}, Lcom/holy/dash/Keep$1;-><init>(Lcom/holy/dash/Keep;Landroid/content/Context;Landroid/content/BroadcastReceiver$PendingResult;)V

    const-string v0, "holy-keep"

    invoke-direct {v1, v2, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    .line 81
    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    goto :goto_e
.end method
