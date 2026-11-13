.class Lcom/holy/dash/MainActivity$Bridge$8;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->bioUnlock()Z
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$1:Lcom/holy/dash/MainActivity$Bridge;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity$Bridge;)V
    .registers 2

    .prologue
    .line 1190
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 7

    .prologue
    const/4 v1, 0x1

    .line 1192
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-boolean v0, v0, Lcom/holy/dash/MainActivity;->bioBusy:Z

    if-eqz v0, :cond_a

    .line 1197
    :goto_9
    return-void

    .line 1193
    :cond_a
    sget-wide v2, Lcom/holy/dash/MainActivity;->unlockedAt:J

    const-wide/16 v4, 0x0

    cmp-long v0, v2, v4

    if-lez v0, :cond_3f

    invoke-static {}, Landroid/os/SystemClock;->elapsedRealtime()J

    move-result-wide v2

    sget-wide v4, Lcom/holy/dash/MainActivity;->unlockedAt:J

    sub-long/2addr v2, v4

    const-wide/32 v4, 0xea60

    cmp-long v0, v2, v4

    if-gez v0, :cond_3f

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    if-eqz v0, :cond_34

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v0, v0, Lcom/holy/dash/MainActivity;->lockView:Landroid/view/View;

    invoke-virtual {v0}, Landroid/view/View;->getVisibility()I

    move-result v0

    if-eqz v0, :cond_3f

    :cond_34
    move v0, v1

    .line 1194
    :goto_35
    if-eqz v0, :cond_41

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->bioOpen()V

    goto :goto_9

    .line 1193
    :cond_3f
    const/4 v0, 0x0

    goto :goto_35

    .line 1195
    :cond_41
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iput-boolean v1, v0, Lcom/holy/dash/MainActivity;->pendingWeb:Z

    .line 1196
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$8;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->askAuth()V

    goto :goto_9
.end method
