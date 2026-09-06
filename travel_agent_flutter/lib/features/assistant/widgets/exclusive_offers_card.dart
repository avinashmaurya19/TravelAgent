import 'package:flutter/material.dart';

/// Exclusive Offers carousel matching the middle promotional banner section of ixigo.
class ExclusiveOffersCard extends StatelessWidget {
  const ExclusiveOffersCard({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Text(
            'Exclusive Offers ✨',
            style: TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.bold,
              fontStyle: FontStyle.italic,
              letterSpacing: 0.5,
            ),
          ),
        ),
        SizedBox(
          height: 96,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12),
            children: [
              // Offer 1: ICICI Bank
              _buildOfferItem(
                gradient: const [Color(0xFF2C1B18), Color(0xFF1E1618)],
                borderColor: const Color(0xFFD32F2F).withOpacity(0.3),
                logoText: 'ICICI Bank',
                logoColor: const Color(0xFFFF5252),
                title: 'Flat 12% Off',
                subtitle: 'with ICICI Bank Credit Card EMI',
                icon: Icons.credit_card_rounded,
                iconColor: const Color(0xFFFF7043),
              ),

              // Offer 2: SalarySe
              _buildOfferItem(
                gradient: const [Color(0xFF1F1B30), Color(0xFF161424)],
                borderColor: const Color(0xFF9C27B0).withOpacity(0.3),
                logoText: 'salaryse',
                logoColor: const Color(0xFFBA68C8),
                title: 'Flat 15% Off',
                subtitle: 'on Flights with SalarySe UPI',
                icon: Icons.discount_rounded,
                iconColor: const Color(0xFFAB47BC),
              ),

              // Offer 3: Zero Convenience
              _buildOfferItem(
                gradient: const [Color(0xFF142426), Color(0xFF101B1C)],
                borderColor: const Color(0xFF00B0FF).withOpacity(0.3),
                logoText: 'ixigo Assured',
                logoColor: const Color(0xFF00E5FF),
                title: '₹0 Convenience Fee',
                subtitle: 'on your first AI travel booking',
                icon: Icons.verified_user_rounded,
                iconColor: const Color(0xFF00E5FF),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildOfferItem({
    required List<Color> gradient,
    required Color borderColor,
    required String logoText,
    required Color logoColor,
    required String title,
    required String subtitle,
    required IconData icon,
    required Color iconColor,
  }) {
    return Container(
      width: 270,
      margin: const EdgeInsets.symmetric(horizontal: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: gradient,
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: borderColor, width: 1),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  logoText,
                  style: TextStyle(
                    color: logoColor,
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 0.5,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  title,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: Color(0xFF9E9E9E),
                    fontSize: 10,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
