import 'package:flutter/material.dart';
import '../model/caregiver.dart';
import '../theme/app_theme.dart';

class CaregiverCard extends StatelessWidget {
  final Caregiver caregiver;
  final VoidCallback onTap;

  const CaregiverCard({
    Key? key,
    required this.caregiver,
    required this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      color: AppColors.lightSageGreen,
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        title: Text(
          caregiver.name,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: AppColors.darkSageGreen,
          ),
        ),
        subtitle: Text(
          'Specialization: ${caregiver.specialization}',
          style: const TextStyle(color: AppColors.darkGray),
        ),
        trailing: const Icon(Icons.arrow_forward, color: AppColors.sageGreen),
        onTap: onTap,
      ),
    );
  }
}
