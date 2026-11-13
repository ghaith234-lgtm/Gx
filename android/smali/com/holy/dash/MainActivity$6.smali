.class Lcom/holy/dash/MainActivity$6;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->showSetup(Ljava/lang/String;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = null
.end annotation


# instance fields
.field final synthetic this$0:Lcom/holy/dash/MainActivity;


# direct methods
.method constructor <init>(Lcom/holy/dash/MainActivity;)V
    .registers 2

    .prologue
    .line 296
    iput-object p1, p0, Lcom/holy/dash/MainActivity$6;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 4

    .prologue
    .line 297
    iget-object v0, p0, Lcom/holy/dash/MainActivity$6;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->connect(Z)V

    return-void
.end method
