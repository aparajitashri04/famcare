import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../model/booking.dart';
import '../theme/app_theme.dart';

class BookingSummaryCard extends StatelessWidget {
  final CartBooking booking;
  final int index;
  final bool showRemoveButton;
  final VoidCallback? onRemove;

  const BookingSummaryCard({
    Key? key,
    required this.booking,
    required this.index,
    this.showRemoveButton = false,
    this.onRemove,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final startTime = DateFormat('h:mm a').format(booking.startTime);

    return Card(
      color: AppColors.lightSageGreen,
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        title: Text(
          booking.serviceName,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: AppColors.darkSageGreen,
          ),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 8),
            Text('${booking.date} at $startTime'),
            const SizedBox(height: 4),
            Text(
              '\$${booking.price.toStringAsFixed(2)}',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: AppColors.sageGreen,
              ),
            ),
          ],
        ),
        trailing: showRemoveButton
            ? IconButton(
                icon: const Icon(Icons.delete_outline, color: AppColors.error),
                onPressed: onRemove,
              )
            : null,
      ),
    );
  }
}
