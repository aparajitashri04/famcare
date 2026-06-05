import 'package:flutter/material.dart';
import '../model/service.dart';
import '../theme/app_theme.dart';

class ServiceCard extends StatelessWidget {
  final Service service;
  final VoidCallback onTap;

  const ServiceCard({
    Key? key,
    required this.service,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.lightSageGreen,
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        title: Text(
          service.name,
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
            Text('Duration: ${service.durationMinutes} minutes'),
            const SizedBox(height: 4),
            Text(
              'Price: \$${service.price.toStringAsFixed(2)}',
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                color: AppColors.sageGreen,
              ),
            ),
          ],
        ),
        trailing: const Icon(Icons.arrow_forward, color: AppColors.sageGreen),
        onTap: onTap,
      ),
    );
  }
}
