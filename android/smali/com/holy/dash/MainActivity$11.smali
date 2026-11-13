.class Lcom/holy/dash/MainActivity$11;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->showError(Ljava/lang/String;)V
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
    .line 605
    iput-object p1, p0, Lcom/holy/dash/MainActivity$11;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/view/View;)V
    .registers 4

    .prologue
    .line 606
    iget-object v0, p0, Lcom/holy/dash/MainActivity$11;->this$0:Lcom/holy/dash/MainActivity;

    invoke-virtual {v0}, Lcom/holy/dash/MainActivity;->hideError()V

    iget-object v0, p0, Lcom/holy/dash/MainActivity$11;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, p0, Lcom/holy/dash/MainActivity$11;->this$0:Lcom/holy/dash/MainActivity;

    iget-object v1, v1, Lcom/holy/dash/MainActivity;->origin:Ljava/lang/String;

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->showSetup(Ljava/lang/String;)V

    return-void
.end method
