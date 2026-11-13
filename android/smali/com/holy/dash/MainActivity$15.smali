.class Lcom/holy/dash/MainActivity$15;
.super Ljava/lang/Object;
.source "MainActivity.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/holy/dash/MainActivity;->askBattery(Z)V
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
    .line 737
    iput-object p1, p0, Lcom/holy/dash/MainActivity$15;->this$0:Lcom/holy/dash/MainActivity;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .registers 5

    .prologue
    .line 738
    iget-object v0, p0, Lcom/holy/dash/MainActivity$15;->this$0:Lcom/holy/dash/MainActivity;

    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Lcom/holy/dash/MainActivity;->askBattery(Z)V

    return-void
.end method
