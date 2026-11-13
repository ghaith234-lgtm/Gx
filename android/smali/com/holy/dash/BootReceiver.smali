.class public Lcom/holy/dash/BootReceiver;
.super Landroid/content/BroadcastReceiver;
.source "BootReceiver.java"


# direct methods
.method public constructor <init>()V
    .registers 1

    .prologue
    .line 8
    invoke-direct {p0}, Landroid/content/BroadcastReceiver;-><init>()V

    return-void
.end method


# virtual methods
.method public onReceive(Landroid/content/Context;Landroid/content/Intent;)V
    .registers 5

    .prologue
    .line 11
    if-nez p2, :cond_1d

    const/4 v0, 0x0

    .line 12
    :goto_3
    const-string v1, "android.intent.action.BOOT_COMPLETED"

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_13

    const-string v1, "android.intent.action.MY_PACKAGE_REPLACED"

    invoke-virtual {v1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_1c

    .line 13
    :cond_13
    invoke-static {p1}, Lcom/holy/dash/Notif;->channels(Landroid/content/Context;)V

    .line 14
    invoke-static {p1}, Lcom/holy/dash/WatchService;->start(Landroid/content/Context;)V

    .line 15
    invoke-static {p1}, Lcom/holy/dash/Keep;->schedule(Landroid/content/Context;)V

    .line 17
    :cond_1c
    return-void

    .line 11
    :cond_1d
    invoke-virtual {p2}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object v0

    goto :goto_3
.end method
