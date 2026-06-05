import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../model/slot.dart';
import '../theme/app_theme.dart';

class SlotCard extends StatelessWidget {
  final Slot slot;
  final String serviceName;
  final double servicePrice;
  final int durationMinutes;
  final String date;
  final VoidCallback onTap;

  const SlotCard({
    Key? key,
    required this.slot,
    required this.serviceName,
    required this.servicePrice,
    required this.durationMinutes,
    required this.date,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final startTime = DateFormat('h:mm a').format(slot.startTime);
    final endTime = DateFormat('h:mm a').format(slot.endTime);

    return Card(
      color: AppColors.lightSageGreen,
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        title: Text(
          '$startTime - $endTime',
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppColors.darkSageGreen,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 8),
            Text('Duration: $durationMinutes minutes'),
            const SizedBox(height: 4),
            Text(
              'Price: \$${servicePrice.toStringAsFixed(2)}',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: AppColors.sageGreen,
              ),
            ),
          ],
        ),
        trailing: const Icon(Icons.add_circle, color: AppColors.sageGreen),
        onTap: onTap,
      ),
    );
  }
}
