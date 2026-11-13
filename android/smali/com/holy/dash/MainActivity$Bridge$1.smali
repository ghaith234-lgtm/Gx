.class Lcom/holy/dash/MainActivity$Bridge$1;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->pair(Ljava/lang/String;Ljava/lang/String;J)V
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
    .line 1105
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .prologue
    .line 1107
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/WatchService;->start(Landroid/content/Context;)V

    .line 1108
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->notifAllowed()Z

    move-result v0

    if-nez v0, :cond_19

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->askNotif()V

    .line 1110
    :cond_18
    :goto_18
    return-void

    .line 1109
    :cond_19
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->askedBattery(Landroid/content/Context;)Z

    move-result v0

    if-nez v0, :cond_18

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    invoke-static {v0}, Lcom/holy/dash/Prefs;->setAskedBattery(Landroid/content/Context;)V

    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$1;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->askBattery(Z)V

    goto :goto_18
.end method
