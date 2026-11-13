.class Lcom/holy/dash/MainActivity$Bridge$11;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Ljava/lang/Runnable;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity$Bridge;->changeServer()V
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
    .line 1230
    iput-object p1, p0, Lcom/holy/dash/MainActivity$Bridge$11;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public run()V
    .registers 3

    .prologue
    .line 1230
    iget-object v0, p0, Lcom/holy/dash/MainActivity$Bridge$11;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v0, v0, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$Bridge$11;->this$1:Lcom/holy/dash/MainActivity$Bridge;

    iget-object v1, v1, Lcom/holy/dash/MainActivity$Bridge;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v1, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->showSetup(Ljava/lang/String;)V

    return-void
.end method
