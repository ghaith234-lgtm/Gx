.class Lcom/holy/dash/WatchService$2;
.super Landroid/net/ConnectivityManager$NetworkCallback;
.source "WatchService.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/WatchService;->listenNetwork()V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/WatchService;


# direct methods
.method constructor <init>(Lcom/holy/dash/WatchService;)V
    .registers 2

    .prologue
    .line 90
    iput-object p1, p0, Lcom/holy/dash/WatchService$2;->this$0:Lcom/holy/dash/WatchService;

    invoke-direct {p0}, Landroid/net/ConnectivityManager$NetworkCallback;-><init>()V

    return-void
.end method


# virtual methods
.method public onAvailable(Landroid/net/Network;)V
    .registers 3

    .prologue
    .line 91
    iget-object v0, p0, Lcom/holy/dash/WatchService$2;->this$0:Lcom/holy/dash/WatchService;

    # invokes: Lcom/holy/dash/WatchService;->kick()V
    invoke-static {v0}, Lcom/holy/dash/WatchService;->access$100(Lcom/holy/dash/WatchService;)V

    return-void
.end method

.method public onLost(Landroid/net/Network;)V
    .registers 3

    .prologue
    .line 92
    iget-object v0, p0, Lcom/holy/dash/WatchService$2;->this$0:Lcom/holy/dash/WatchService;

    # invokes: Lcom/holy/dash/WatchService;->kick()V
    invoke-static {v0}, Lcom/holy/dash/WatchService;->access$100(Lcom/holy/dash/WatchService;)V

    return-void
.end method
