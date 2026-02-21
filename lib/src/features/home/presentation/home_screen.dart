import 'package:flutter/material.dart';
import '../../../shared/theme/responsive_layout.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VokVision Home'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {},
          ),
        ],
      ),
      body: GridView.count(
        crossAxisCount: context.responsiveValue(mobile: 2, tablet: 3, desktop: 4).toInt(),
        padding: EdgeInsets.all(context.widthPct(4)),
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        children: [
          _buildFeatureCard(
            context,
            'New Capture',
            Icons.add_a_photo_rounded,
            Colors.blue,
          ),
          _buildFeatureCard(
            context,
            'Gallery',
            Icons.dashboard_rounded,
            Colors.green,
          ),
          _buildFeatureCard(
            context,
            'Reconstructions',
            Icons.model_training_rounded,
            Colors.orange,
          ),
          _buildFeatureCard(
            context,
            'Editor',
            Icons.edit_rounded,
            Colors.purple,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        label: const Text('Quick Capture'),
        icon: const Icon(Icons.camera),
      ),
    );
  }

  Widget _buildFeatureCard(
      BuildContext context, String title, IconData icon, Color color) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () {},
        borderRadius: BorderRadius.circular(16),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 48, color: color),
            const SizedBox(height: 12),
            Text(
              title,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }
}
