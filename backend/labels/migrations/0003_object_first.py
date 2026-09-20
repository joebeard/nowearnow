import django.db.models.deletion
from django.db import migrations, models


def attach_generic_objects(apps, schema_editor):
    Label = apps.get_model("labels", "Label")
    Item = apps.get_model("labels", "Item")
    for label in Label.objects.filter(item__isnull=True).iterator():
        item = Item.objects.create(
            profile_id=label.profile_id, name="General belongings", kind="group"
        )
        label.item_id = item.pk
        label.save(update_fields=["item"])


class Migration(migrations.Migration):
    dependencies = [("labels", "0002_alter_access_options_alter_delivery_options_and_more")]
    operations = [
        migrations.AddField(
            model_name="item",
            name="kind",
            field=models.CharField(
                choices=[("item", "Specific item"), ("group", "Reusable group of belongings")],
                default="item",
                max_length=10,
            ),
        ),
        migrations.RunPython(attach_generic_objects, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="label",
            name="item",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, related_name="label", to="labels.item"
            ),
        ),
    ]
