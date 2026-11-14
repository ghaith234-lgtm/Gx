.class public Lcom/holy/dash/WatchService;
.super Landroid/app/Service;
.source "WatchService.java"


# static fields
.field static volatile RUNNING:Z


# instance fields
.field private volatile byUser:Z

.field private final cur:[Ljava/net/HttpURLConnection;

.field private fgText:Ljava/lang/String;

.field private loop:Ljava/lang/Thread;

.field private netCb:Landroid/net/ConnectivityManager$NetworkCallback;

.field private volatile run:Z


# direct methods
.method public constructor <init>()V
    .registers 2

    .prologue
    .line 23
    invoke-direct {p0}, Landroid/app/Service;-><init>()V

    .line 28
    const/4 v0, 0x1

    new-array v0, v0, [Ljava/net/HttpURLConnection;

    iput-object v0, p0, Lcom/holy/dash/WatchService;->cur:[Ljava/net/HttpURLConnection;

    .line 30
    const-string v0, ""

    iput-object v0, p0, Lcom/holy/dash/WatchService;->fgText:Ljava/lang/String;

    return-void
.end method

.method static synthetic access$000(Lcom/holy/dash/WatchService;)V
    .registers 1

    .prologue
    .line 23
    invoke-direct {p0}, Lcom/holy/dash/WatchService;->watch()V

    return-void
.end method

.method static synthetic access$100(Lcom/holy/dash/WatchService;)V
    .registers 1

    .prologue
    .line 23
    invoke-direct {p0}, Lcom/holy/dash/WatchService;->kick()V

    return-void
.end method

.method private foreground(Ljava/lang/String;)V
    .registers 5

    .prologue
    .line 75
    iget-object v0, p0, Lcom/holy/dash/WatchService;->fgText:Ljava/lang/String;

    invoke-virtual {p1, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_9

    .line 84
    :goto_8
    return-void

    .line 76
    :cond_9
    iput-object p1, p0, Lcom/holy/dash/WatchService;->fgText:Ljava/lang/String;

    .line 77
    invoke-static {p0, p1}, Lcom/holy/dash/Notif;->watching(Landroid/content/Context;Ljava/lang/String;)Landroid/app/Notification;

    move-result-object v0

    .line 79
    :try_start_f
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x22

    if-lt v1, v2, :cond_21

    const/4 v1, 0x1

    const/high16 v2, 0x40000000    # 2.0f

    invoke-virtual {p0, v1, v0, v2}, Lcom/holy/dash/WatchService;->startForeground(ILandroid/app/Notification;I)V
    :try_end_1b
    .catch Ljava/lang/Exception; {:try_start_f .. :try_end_1b} :catch_1c

    goto :goto_8

    .line 81
    :catch_1c
    move-exception v0

    .line 82
    invoke-virtual {p0}, Lcom/holy/dash/WatchService;->stopSelf()V

    goto :goto_8

    .line 80
    :cond_21
    const/4 v1, 0x1

    :try_start_22
    invoke-virtual {p0, v1, v0}, Lcom/holy/dash/WatchService;->startForeground(ILandroid/app/Notification;)V
    :try_end_25
    .catch Ljava/lang/Exception; {:try_start_22 .. :try_end_25} :catch_1c

    goto :goto_8
.end method

.method private kick()V
    .registers 3

    .prologue
    .line 101
    iget-object v0, p0, Lcom/holy/dash/WatchService;->cur:[Ljava/net/HttpURLConnection;

    const/4 v1, 0x0

    aget-object v0, v0, v1

    .line 102
    if-eqz v0, :cond_a

    .line 103
    :try_start_7
    invoke-virtual {v0}, Ljava/net/HttpURLConnection;->disconnect()V
    :try_end_a
    .catch Ljava/lang/Exception; {:try_start_7 .. :try_end_a} :catch_b

    .line 105
    :cond_a
    :goto_a
    return-void

    .line 103
    :catch_b
    move-exception v0

    goto :goto_a
.end method

.method private listenNetwork()V
    .registers 3

    .prologue
    .line 89
    :try_start_0
    const-string v0, "connectivity"

    invoke-virtual {p0, v0}, Lcom/holy/dash/WatchService;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/net/ConnectivityManager;

    .line 90
    new-instance v1, Lcom/holy/dash/WatchService$2;

    invoke-direct {v1, p0}, Lcom/holy/dash/WatchService$2;-><init>(Lcom/holy/dash/WatchService;)V

    iput-object v1, p0, Lcom/holy/dash/WatchService;->netCb:Landroid/net/ConnectivityManager$NetworkCallback;

    .line 94
    iget-object v1, p0, Lcom/holy/dash/WatchService;->netCb:Landroid/net/ConnectivityManager$NetworkCallback;

    invoke-virtual {v0, v1}, Landroid/net/ConnectivityManager;->registerDefaultNetworkCallback(Landroid/net/ConnectivityManager$NetworkCallback;)V
    :try_end_14
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_14} :catch_15

    .line 98
    :goto_14
    return-void

    .line 95
    :catch_15
    move-exception v0

    .line 96
    const/4 v0, 0x0

    iput-object v0, p0, Lcom/holy/dash/WatchService;->netCb:Landroid/net/ConnectivityManager$NetworkCallback;

    goto :goto_14
.end method

.method static start(Landroid/content/Context;)V
    .registers 4

    .prologue
    .line 33
    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_c

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_d

    .line 41
    :cond_c
    :goto_c
    return-void

    .line 34
    :cond_d
    new-instance v0, Landroid/content/Intent;

    const-class v1, Lcom/holy/dash/WatchService;

    invoke-direct {v0, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    .line 36
    :try_start_14
    sget v1, Landroid/os/Build$VERSION;->SDK_INT:I

    const/16 v2, 0x1a

    if-lt v1, v2, :cond_20

    invoke-virtual {p0, v0}, Landroid/content/Context;->startForegroundService(Landroid/content/Intent;)Landroid/content/ComponentName;

    goto :goto_c

    .line 38
    :catch_1e
    move-exception v0

    goto :goto_c

    .line 37
    :cond_20
    invoke-virtual {p0, v0}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    :try_end_23
    .catch Ljava/lang/Exception; {:try_start_14 .. :try_end_23} :catch_1e

    goto :goto_c
.end method

.method static stop(Landroid/content/Context;)V
    .registers 3

    .prologue
    .line 44
    invoke-static {p0}, Lcom/holy/dash/Keep;->cancel(Landroid/content/Context;)V

    .line 45
    new-instance v0, Landroid/content/Intent;

    const-class v1, Lcom/holy/dash/WatchService;

    invoke-direct {v0, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    invoke-virtual {p0, v0}, Landroid/content/Context;->stopService(Landroid/content/Intent;)Z

    .line 46
    return-void
.end method

.method private watch()V
    .registers 12

    .prologue
    const/4 v10, 0x3

    const/4 v9, 0x1

    const/4 v1, 0x0

    .line 108
    sput-boolean v9, Lcom/holy/dash/WatchService;->RUNNING:Z

    .line 110
    const-string v0, "power"

    invoke-virtual {p0, v0}, Lcom/holy/dash/WatchService;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/os/PowerManager;

    .line 111
    const-string v2, "holy:feed"

    invoke-virtual {v0, v9, v2}, Landroid/os/PowerManager;->newWakeLock(ILjava/lang/String;)Landroid/os/PowerManager$WakeLock;

    move-result-object v4

    .line 112
    invoke-virtual {v4, v1}, Landroid/os/PowerManager$WakeLock;->setReferenceCounted(Z)V

    move v0, v1

    .line 113
    :goto_17
    iget-boolean v2, p0, Lcom/holy/dash/WatchService;->run:Z

    if-eqz v2, :cond_37

    .line 114
    invoke-static {p0}, Lcom/holy/dash/Prefs;->origin(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v2

    invoke-static {p0}, Lcom/holy/dash/Prefs;->token(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v3

    .line 115
    invoke-virtual {v2}, Ljava/lang/String;->isEmpty()Z

    move-result v5

    if-nez v5, :cond_35

    invoke-virtual {v3}, Ljava/lang/String;->isEmpty()Z

    move-result v5

    if-nez v5, :cond_35

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v5

    if-nez v5, :cond_3f

    :cond_35
    iput-boolean v9, p0, Lcom/holy/dash/WatchService;->byUser:Z

    .line 144
    :cond_37
    :goto_37
    iput-boolean v1, p0, Lcom/holy/dash/WatchService;->run:Z

    .line 145
    sput-boolean v1, Lcom/holy/dash/WatchService;->RUNNING:Z

    .line 146
    invoke-virtual {p0}, Lcom/holy/dash/WatchService;->stopSelf()V

    .line 147
    return-void

    .line 116
    :cond_3f
    invoke-static {p0}, Lcom/holy/dash/Prefs;->lastId(Landroid/content/Context;)J

    move-result-wide v6

    .line 118
    :try_start_43
    new-instance v5, Ljava/util/HashMap;

    invoke-direct {v5}, Ljava/util/HashMap;-><init>()V

    .line 119
    const-string v8, "X-Holy-Device"

    invoke-interface {v5, v8, v3}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 120
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, "/api/app/feed?since="

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v6, v7}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, "&wait=50"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    const v3, 0x124f8

    iget-object v6, p0, Lcom/holy/dash/WatchService;->cur:[Ljava/net/HttpURLConnection;

    invoke-static {v2, v5, v3, v6}, Lcom/holy/dash/Net;->get(Ljava/lang/String;Ljava/util/Map;I[Ljava/net/HttpURLConnection;)Lcom/holy/dash/Net$Resp;

    move-result-object v2

    .line 121
    iget v3, v2, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v5, 0x191

    if-eq v3, v5, :cond_7f

    iget v3, v2, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v5, 0x193

    if-ne v3, v5, :cond_9f

    .line 122
    :cond_7f
    invoke-static {p0, v2}, Lcom/holy/dash/Feed;->handle(Landroid/content/Context;Lcom/holy/dash/Net$Resp;)I

    .line 123
    const/4 v2, 0x1

    iput-boolean v2, p0, Lcom/holy/dash/WatchService;->byUser:Z
    :try_end_85
    .catch Ljava/lang/Exception; {:try_start_43 .. :try_end_85} :catch_86

    goto :goto_37

    .line 136
    :catch_86
    move-exception v2

    .line 137
    :goto_87
    iget-boolean v2, p0, Lcom/holy/dash/WatchService;->run:Z

    if-eqz v2, :cond_37

    .line 138
    add-int/lit8 v0, v0, 0x1

    .line 139
    if-lt v0, v10, :cond_94

    const-string v2, "\u063a\u064a\u0631 \u0645\u062a\u0635\u0644 \u0628\u0627\u0644\u0644\u0648\u062d\u0629 \u2014 \u062c\u0627\u0631\u064d \u0625\u0639\u0627\u062f\u0629 \u0627\u0644\u0645\u062d\u0627\u0648\u0644\u0629\u2026"

    invoke-direct {p0, v2}, Lcom/holy/dash/WatchService;->foreground(Ljava/lang/String;)V

    .line 140
    :cond_94
    if-gt v0, v9, :cond_dd

    const-wide/16 v2, 0xbb8

    .line 141
    :goto_98
    :try_start_98
    invoke-static {v2, v3}, Ljava/lang/Thread;->sleep(J)V
    :try_end_9b
    .catch Ljava/lang/InterruptedException; {:try_start_98 .. :try_end_9b} :catch_9d

    goto/16 :goto_17

    :catch_9d
    move-exception v0

    goto :goto_37

    .line 126
    :cond_9f
    :try_start_9f
    iget v3, v2, Lcom/holy/dash/Net$Resp;->code:I

    const/16 v5, 0xc8

    if-eq v3, v5, :cond_c0

    new-instance v3, Ljava/io/IOException;

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "HTTP "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    iget v2, v2, Lcom/holy/dash/Net$Resp;->code:I

    invoke-virtual {v5, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-direct {v3, v2}, Ljava/io/IOException;-><init>(Ljava/lang/String;)V

    throw v3

    .line 127
    :cond_c0
    const-wide/16 v6, 0x3a98

    invoke-virtual {v4, v6, v7}, Landroid/os/PowerManager$WakeLock;->acquire(J)V
    :try_end_c5
    .catch Ljava/lang/Exception; {:try_start_9f .. :try_end_c5} :catch_86

    .line 129
    :try_start_c5
    invoke-static {p0, v2}, Lcom/holy/dash/Feed;->handle(Landroid/content/Context;Lcom/holy/dash/Net$Resp;)I
    :try_end_c8
    .catchall {:try_start_c5 .. :try_end_c8} :catchall_d8

    .line 131
    :try_start_c8
    invoke-virtual {v4}, Landroid/os/PowerManager$WakeLock;->release()V

    .line 133
    if-lez v0, :cond_d2

    const-string v2, "\u0645\u062a\u0635\u0644 \u0628\u0644\u0648\u062d\u062a\u0643"

    invoke-direct {p0, v2}, Lcom/holy/dash/WatchService;->foreground(Ljava/lang/String;)V
    :try_end_d2
    .catch Ljava/lang/Exception; {:try_start_c8 .. :try_end_d2} :catch_86

    .line 135
    :cond_d2
    :try_start_d2
    invoke-static {p0}, Lcom/holy/dash/HolyWidget;->tick(Landroid/content/Context;)V
    :try_end_d5
    .catch Ljava/lang/Exception; {:try_start_d2 .. :try_end_d5} :catch_f3

    move v0, v1

    .line 142
    goto/16 :goto_17

    .line 131
    :catchall_d8
    move-exception v2

    :try_start_d9
    invoke-virtual {v4}, Landroid/os/PowerManager$WakeLock;->release()V

    .line 132
    throw v2
    :try_end_dd
    .catch Ljava/lang/Exception; {:try_start_d9 .. :try_end_dd} :catch_86

    .line 140
    :cond_dd
    const/4 v2, 0x2

    if-ne v0, v2, :cond_e3

    const-wide/16 v2, 0x1770

    goto :goto_98

    :cond_e3
    if-ne v0, v10, :cond_e8

    const-wide/16 v2, 0x2ee0

    goto :goto_98

    :cond_e8
    const/16 v2, 0x8

    if-ge v0, v2, :cond_ef

    const-wide/16 v2, 0x7530

    goto :goto_98

    :cond_ef
    const-wide/32 v2, 0xea60

    goto :goto_98

    .line 136
    :catch_f3
    move-exception v0

    move v0, v1

    goto :goto_87
.end method


# virtual methods
.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .registers 3

    .prologue
    .line 172
    const/4 v0, 0x0

    return-object v0
.end method

.method public onCreate()V
    .registers 1

    .prologue
    .line 50
    invoke-super {p0}, Landroid/app/Service;->onCreate()V

    .line 51
    invoke-static {p0}, Lcom/holy/dash/Notif;->channels(Landroid/content/Context;)V

    .line 52
    return-void
.end method

.method public onDestroy()V
    .registers 3

    .prologue
    const/4 v1, 0x0

    .line 158
    iget-boolean v0, p0, Lcom/holy/dash/WatchService;->run:Z

    .line 159
    iput-boolean v1, p0, Lcom/holy/dash/WatchService;->run:Z

    .line 160
    sput-boolean v1, Lcom/holy/dash/WatchService;->RUNNING:Z

    .line 161
    if-eqz v0, :cond_1e

    iget-boolean v0, p0, Lcom/holy/dash/WatchService;->byUser:Z

    if-nez v0, :cond_1e

    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_1e

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v0

    if-eqz v0, :cond_1e

    const-wide/16 v0, 0x1388

    invoke-static {p0, v0, v1}, Lcom/holy/dash/Keep;->soon(Landroid/content/Context;J)V

    .line 162
    :cond_1e
    invoke-direct {p0}, Lcom/holy/dash/WatchService;->kick()V

    .line 163
    iget-object v0, p0, Lcom/holy/dash/WatchService;->loop:Ljava/lang/Thread;

    if-eqz v0, :cond_2a

    iget-object v0, p0, Lcom/holy/dash/WatchService;->loop:Ljava/lang/Thread;

    invoke-virtual {v0}, Ljava/lang/Thread;->interrupt()V

    .line 164
    :cond_2a
    iget-object v0, p0, Lcom/holy/dash/WatchService;->netCb:Landroid/net/ConnectivityManager$NetworkCallback;

    if-eqz v0, :cond_3b

    .line 165
    :try_start_2e
    const-string v0, "connectivity"

    invoke-virtual {p0, v0}, Lcom/holy/dash/WatchService;->getSystemService(Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/net/ConnectivityManager;

    iget-object v1, p0, Lcom/holy/dash/WatchService;->netCb:Landroid/net/ConnectivityManager$NetworkCallback;

    invoke-virtual {v0, v1}, Landroid/net/ConnectivityManager;->unregisterNetworkCallback(Landroid/net/ConnectivityManager$NetworkCallback;)V
    :try_end_3b
    .catch Ljava/lang/Exception; {:try_start_2e .. :try_end_3b} :catch_3f

    .line 168
    :cond_3b
    :goto_3b
    invoke-super {p0}, Landroid/app/Service;->onDestroy()V

    .line 169
    return-void

    .line 166
    :catch_3f
    move-exception v0

    goto :goto_3b
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .registers 8

    .prologue
    const/4 v0, 0x1

    .line 56
    const-string v1, "\u0645\u062a\u0635\u0644 \u0628\u0644\u0648\u062d\u062a\u0643"

    invoke-direct {p0, v1}, Lcom/holy/dash/WatchService;->foreground(Ljava/lang/String;)V

    .line 57
    invoke-static {p0}, Lcom/holy/dash/Prefs;->paired(Landroid/content/Context;)Z

    move-result v1

    if-eqz v1, :cond_12

    invoke-static {p0}, Lcom/holy/dash/Prefs;->watch(Landroid/content/Context;)Z

    move-result v1

    if-nez v1, :cond_19

    .line 58
    :cond_12
    iput-boolean v0, p0, Lcom/holy/dash/WatchService;->byUser:Z

    .line 59
    invoke-virtual {p0}, Lcom/holy/dash/WatchService;->stopSelf()V

    .line 60
    const/4 v0, 0x2

    .line 71
    :cond_18
    :goto_18
    return v0

    .line 62
    :cond_19
    invoke-static {p0}, Lcom/holy/dash/Keep;->schedule(Landroid/content/Context;)V

    .line 63
    iget-object v1, p0, Lcom/holy/dash/WatchService;->loop:Ljava/lang/Thread;

    if-eqz v1, :cond_28

    iget-object v1, p0, Lcom/holy/dash/WatchService;->loop:Ljava/lang/Thread;

    invoke-virtual {v1}, Ljava/lang/Thread;->isAlive()Z

    move-result v1

    if-nez v1, :cond_18

    .line 64
    :cond_28
    iput-boolean v0, p0, Lcom/holy/dash/WatchService;->run:Z

    .line 65
    new-instance v1, Ljava/lang/Thread;

    new-instance v2, Lcom/holy/dash/WatchService$1;

    invoke-direct {v2, p0}, Lcom/holy/dash/WatchService$1;-><init>(Lcom/holy/dash/WatchService;)V

    const-string v3, "holy-watch"

    invoke-direct {v1, v2, v3}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    iput-object v1, p0, Lcom/holy/dash/WatchService;->loop:Ljava/lang/Thread;

    .line 68
    iget-object v1, p0, Lcom/holy/dash/WatchService;->loop:Ljava/lang/Thread;

    invoke-virtual {v1}, Ljava/lang/Thread;->start()V

    .line 69
    invoke-direct {p0}, Lcom/holy/dash/WatchService;->listenNetwork()V

    goto :goto_18
.end method

.method public onTaskRemoved(Landroid/content/Intent;)V
    .registers 4

    .prologue
    .line 152
    const-wide/16 v0, 0x7d0

    invoke-static {p0, v0, v1}, Lcom/holy/dash/Keep;->soon(Landroid/content/Context;J)V

    .line 153
    invoke-super {p0, p1}, Landroid/app/Service;->onTaskRemoved(Landroid/content/Intent;)V

    .line 154
    return-void
.end method
