.class Lcom/holy/dash/WatchService$1;
.super Ljava/lang/Object;
.source "WatchService.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/WatchService;->onStartCommand(Landroid/content/Intent;II)I
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
    .line 65
    iput-object p1, p0, Lcom/holy/dash/WatchService$1;->this$0:Lcom/holy/dash/WatchService;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 2

    .prologue
    .line 66
    iget-object v0, p0, Lcom/holy/dash/WatchService$1;->this$0:Lcom/holy/dash/WatchService;

    # invokes: Lcom/holy/dash/WatchService;->watch()V
    invoke-static {v0}, Lcom/holy/dash/WatchService;->access$000(Lcom/holy/dash/WatchService;)V

    return-void
.end method
